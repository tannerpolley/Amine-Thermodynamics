"""Effect of printed parameter precision on the joint-fit statistics (#207). Every coefficient of the reported record is
rounded to 4 or 6 significant figures, as a reader copying the manuscript tables would obtain, and the 307 objective rows
are replayed with the A7 fit specification and weights. Fixed parameters, no fit. Writes
results/engine-3e83e19c-paper-evidence/parameter-rounding/; run from the checkout root with `nice -n 10`. The historical
results/parameter-rounding/ (record e234e860) came from this script at commit 0ebdf6c, whose inputs stay in Git history."""
import concurrent.futures as cf, copy, csv, json, math, os, sys
from pathlib import Path
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
B = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(B / 'scripts'), str(B / 'calibration-misfit'), str(B.parents[1] / 'src')]
import a7_presentation as a, fit_campaign as c, fit_observations as o

SPEC = B / 'results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/spec.json'  # the specification of the retained replay
RETAINED = B / 'results/engine-3e83e19c-paper-evidence/full-replay.json'
OUT = B / 'results/engine-3e83e19c-paper-evidence/parameter-rounding'
DIGITS = (None, 8, 7, 6, 4)


def rounded(digits):
    record = json.loads(a.SELECTED.read_text())
    if digits:
        for key in ('components', 'pairs', 'correlations', 'model_coefficients', 'reaction_correlations', 'topology'):
            for _, node in a.coefficients(record[key]):
                node['value']['magnitude'] = float(f"{node['value']['magnitude']:.{digits}g}")
    path = OUT / f'parameters-{digits or "full"}.json'
    path.write_text(json.dumps(record, indent=2) + '\n')
    return path


def replay(digits):
    spec = c.load(SPEC)
    mapping = o.s.parameter_mapping(rounded(digits))
    _, rows = o.stage6_rows(spec, mapping)
    weights = c.stage6_weights(spec, [r for r, _ in rows], 1.)
    values = o.replay(mapping, [(r['id'], item, w) for (r, item), w in zip(rows, weights, strict=True)])
    assert len(values) == 307 and all(v['status'] == 'Available' for v in values)
    return digits, values


def statistics(values, groups, loaded):
    by = {}
    for v in values:
        by.setdefault(groups[v['target']], []).append(v)
    out = {g: 100 * math.fsum(abs(v['predicted'] / v['observed'] - 1) for v in part) / len(part) for g, part in by.items() if not g.startswith(('Cai', 'common149 heat'))}
    for g in ('Cai temperature', 'Cai mole_fraction', 'common149 heat'):
        e = [(v['predicted'] - v['observed']) / (1000 if 'heat' in g else 1) for v in by[g]]
        out[g + ' RMSE'] = math.sqrt(math.fsum(x * x for x in e) / len(e))
    out['loaded within 2s'] = sum(abs(v['residual']) <= 2 for v in values if v['target'] in loaded)
    out['total cost'] = math.fsum(v['cost'] for v in values)
    return out


def main():
    OUT.mkdir(exist_ok=True)
    c.verify(c.load(SPEC))  # pinned wheel installed and spec inputs hashed
    fitted = a.rows(a.E / 'fitted-rows.csv')
    groups = {r['id']: (f"{r['group']} {dict(PartialPressure='pressure', PhaseMoleFraction='species', AdditionEnthalpy='heat')[r['quantity']]}"
                        if r['group'] == 'common149' else f"Cai {r['quantity']}" if r['group'] == 'Cai' else r['group']) for r in fitted}
    loaded = set(c.load(SPEC)['loaded_density_ids'])
    with cf.ProcessPoolExecutor(len(DIGITS)) as pool:
        runs = dict(pool.map(replay, DIGITS))
    retained = {v['target']: v for v in json.loads(RETAINED.read_text())}
    assert all(v['predicted'] == retained[v['target']]['predicted'] for v in runs[None])  # full precision equals the retained replay exactly
    full = {v['target']: v['predicted'] for v in runs[None]}
    summary = dict(parameter_sha256=a.INPUTS.get(str(a.SELECTED.relative_to(a.ROOT))) or o.s.sha256(a.SELECTED), engine_commit=o.s.ENGINE_COMMIT,
                   engine_wheel_sha256=o.s.ENGINE_WHEEL_SHA256, statistics={}, max_relative_prediction_change={})
    for digits, values in runs.items():
        name = f'{digits} significant figures' if digits else 'full precision'
        summary['statistics'][name] = statistics(values, groups, loaded)
        if digits:
            summary['max_relative_prediction_change'][name] = max(abs(v['predicted'] / full[v['target']] - 1) for v in values)
        with (OUT / f'replay-{digits or "full"}.csv').open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['target', 'group', 'observed', 'predicted', 'residual', 'cost'])
            w.writeheader()
            w.writerows({k: v[k] for k in w.fieldnames if k in v} | {'group': groups[v['target']]} for v in values)
    o.s.write_json(OUT / 'summary.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
