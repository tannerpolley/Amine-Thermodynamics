"""#391: recompute retained Part I and DEA results on the pinned wheel in ignored run directories; compare with retained values.

Run each from the repository root as a background shell:
  agent-heavy env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src uv run --no-sync python -u \\
      analyses/wheel_recheck_391.py part-i <action> <run directory>
  ... analyses/wheel_recheck_391.py dea <run directory>
  ... analyses/wheel_recheck_391.py compare <run directory> <retained directory> <summary JSON>
  ... analyses/wheel_recheck_391.py deviations <run deviations.json> <retained deviations.json> <summary JSON>

Part I is paper_evidence_341 unchanged, with its output directory moved to the run directory and the #297 wheel binding
replaced by the current pin. Its actions run in its documented order: replay evidence uncertainty comparison weights
shared checks stability. `uncertainty` recomputes only the fit-free adopted-point Jacobian and prediction derivatives;
the conditional fit and profiles are fits and are not rerun. No retained file is written.
"""
import csv
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEA = ROOT/'analyses/dea_transfer'


def part_i(action, run):
    sys.path.insert(0, str(ROOT/'analyses/mea_parameter_bundle/scripts'))
    import shared_evaluation as s
    commit, sha = s.ENGINE_COMMIT, s.ENGINE_WHEEL_SHA256  # the current pin, read before adoption_297 rebinds #297's wheel
    import paper_evidence_341 as pe
    import subprocess
    a, r = pe.a, pe.r
    wheel = r.ROOT/f'build/engine-wheels/main-{commit}/epcsaft-1.3.1-cp313-cp313-manylinux_2_39_x86_64.whl'
    a.COMMIT, a.SHA, a.WHEEL = commit, sha, wheel
    r.COMMIT, r.SHA, r.WHEEL = commit, sha, wheel
    s.ENGINE_COMMIT, s.ENGINE_WHEEL_SHA256 = commit, sha
    historical_verify = a.verify
    def verify():  # adoption_297.verify, with ancestry in the public Engine repository that owns 05e94210
        main = Path(subprocess.check_output(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], cwd=ROOT, text=True).strip()).parent
        subprocess.check_output(['git', '-C', str(main/'upstream/epcsaft'), 'merge-base', '--is-ancestor', commit, 'origin/main'])
        check, a.subprocess = a.subprocess, type('git', (), {'check_output': staticmethod(lambda *args, **kwargs: b'')})
        try:
            historical_verify()
        finally:
            a.subprocess = check
    a.verify = verify
    pe.OUT = Path(run).resolve()
    pe.setup()
    if action == 'uncertainty':
        import uncertainty_307 as u
        class NoFit(Exception):
            pass
        def fit(*args, **kwargs):
            raise NoFit
        u.fit = fit
        try:
            pe.uncertainty()
        except NoFit:
            pass
        spec, _, out = u.setup('MEA')
        predictions = u.prediction_records(spec, 'MEA')
        ev = u.derivative(spec, predictions)
        u.write(out/'predictions.json', dict(records=[{k: x.get(k) for k in ('identity', 'group', 'kind', 'row', 'arguments')} for x in predictions],
                                              values=ev.predictions, gradient=ev.optimizer_gradient))
    else:
        getattr(pe, action)()


def dea(run):
    sys.path.insert(0, str(ROOT/'analyses'))
    import part_ii
    route = part_ii.Route(DEA/'inputs/part-ii-346/route-current.json', run)
    point = json.loads((DEA/'results/retransfer-346/f2-current/report-point.json').read_text())['point']
    rows, available, cost = route.replay(point)
    route.write('replay.json', dict(rows=rows, available=available, cost=cost))
    route.reduce(point)
    route.uncertainty(point)
    route.curves(point)
    route.write('search-summary.json', route.search(point))


def flatten(value, prefix=''):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from flatten(v, f'{prefix}/{k}')
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from flatten(v, f'{prefix}/{i}')
    else:
        yield prefix, value


def number(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load(path):
    if path.suffix == '.csv':
        return list(csv.DictReader(path.open()))
    import gzip
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())


TIME = ('seconds', 'elapsed', 'time', 'heartbeat', 'started', 'finished', 'wall')
ZERO = 1e-12  # reporting split only: pairs with both magnitudes below it are counted as numerical-zero pairs


def field(key):
    names = [part for part in key.split('/') if part and not part.isdigit()]
    return names[-1] if names else key


def compare(run, retained):
    """Every value of every JSON/CSV file present in both trees, aggregated by field name.

    Wall-clock fields and pairs below ZERO in magnitude are reported separately; other numeric differences give
    the largest absolute and relative difference with one example location; non-numeric differences are listed."""
    run, retained = Path(run), Path(retained)
    out = dict(files_compared=0, files_not_retained=[], fields={})
    for path in sorted(p for p in run.rglob('*') if p.suffix in ('.json', '.csv', '.gz') and p.is_file()):
        name = path.relative_to(run)
        if not (retained/name).exists():
            out['files_not_retained'].append(str(name))
            continue
        new, old = dict(flatten(load(path))), dict(flatten(load(retained/name)))
        out['files_compared'] += 1
        for key in new.keys() | old.keys():
            f = out['fields'].setdefault(field(key), dict(values=0, exact=0, missing=0, wall_clock=0, numerical_zero=0, text=0,
                                                         max_abs=0., max_rel=0., at=None, text_examples=[]))
            f['values'] += 1
            if key not in new or key not in old:
                f['missing'] += 1
                continue
            a, b = new[key], old[key]
            if a == b:
                f['exact'] += 1
            elif any(word in field(key).lower() for word in TIME):
                f['wall_clock'] += 1
            elif (x := number(a)) is None or (y := number(b)) is None or not (math.isfinite(x) and math.isfinite(y)):
                f['text'] += 1
                if len(f['text_examples']) < 3:
                    f['text_examples'].append([f'{name}:{key}', a, b])
            elif max(abs(x), abs(y)) < ZERO:
                f['numerical_zero'] += 1
            else:
                d, rel = abs(x-y), abs(x-y)/max(abs(x), abs(y))
                f['max_abs'] = max(f['max_abs'], d)
                if rel > f['max_rel']:
                    f['max_rel'], f['at'] = rel, [f'{name}:{key}', a, b]
    return out


def deviations(run, retained):
    """Part II deviation rows matched by group, role, unit, range and range side; `compare` pairs them by position,
    which is wrong here because their order follows a set and differs between runs."""
    key = lambda r: (r['group'], r['role'], r['unit'], r['range_name'], str(r['outside_range']))
    new, old = ({key(r): r for r in load(Path(p))} for p in (run, retained))
    out = dict(groups=len(new), retained_groups=len(old), same_groups=new.keys() == old.keys(), count_mismatches=0,
               statistics=0, max_rel=0., at=None)
    for k in new.keys() & old.keys():
        a, b = new[k], old[k]
        out['count_mismatches'] += (a['rows'], a['available']) != (b['rows'], b['available'])
        sa, sb = a['statistics'] or {}, b['statistics'] or {}
        for name in sa.keys() & sb.keys():
            x, y = number(sa[name]), number(sb[name])
            if x is None or y is None:
                continue
            out['statistics'] += 1
            rel = abs(x-y)/max(abs(x), abs(y)) if max(abs(x), abs(y)) >= ZERO else 0.
            if rel > out['max_rel']:
                out['max_rel'], out['at'] = rel, [list(k), name, sa[name], sb[name]]
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'part-i':
        part_i(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'dea':
        dea(sys.argv[2])
    elif sys.argv[1] in ('compare', 'deviations'):
        result = (compare if sys.argv[1] == 'compare' else deviations)(sys.argv[2], sys.argv[3])
        if sys.argv[1] == 'deviations':
            Path(sys.argv[4]).write_text(json.dumps(result, indent=1)+'\n')
            sys.exit(print(result))
        Path(sys.argv[4]).parent.mkdir(parents=True, exist_ok=True)
        Path(sys.argv[4]).write_text(json.dumps(result, indent=1)+'\n')
        print(result['files_compared'], 'files compared;', len(result['files_not_retained']), 'not retained')
        for name, f in sorted(result['fields'].items(), key=lambda item: -item[1]['max_rel']):
            if f['exact'] < f['values']:
                print(name, {k: v for k, v in f.items() if k != 'text_examples'}, f['text_examples'][:1])
    else:
        raise ValueError('Expected part-i, dea, compare or deviations')
