import ast, csv, hashlib, json, math, time
from pathlib import Path
import numpy as np
import epcsaft
from epcsaft import equilibrium as eq, regression as reg

REPO = Path(__file__).resolve().parents[2]
AN = REPO / 'analyses/amp_transfer'
OUT = AN / 'results/retransfer-344-05e94210/pure-binary-on-05e94210.json'
AMP, W = 'aminomethylpropanol', 'water'

def load_functions(filename, wanted, scope):
    tree = ast.parse((AN / filename).read_text())
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    assert {f.name for f in funcs} == set(wanted)
    exec(compile(ast.Module(body=funcs, type_ignores=[]), filename, 'exec'), scope)

# Reuse the producer's evaluation routines without executing their top-level fitting campaign.
load_functions('pure_fit.py', {'observation', 'assess'}, globals())
load_functions('binary.py', {'bubble', 'predictions'}, globals())

started = time.perf_counter()
rows = list(csv.DictReader((AN / 'inputs/pure-amp.csv').open()))
pure_doc = json.loads((AN / 'inputs/amp-pure-endpoint.json').read_text())
pure_assessment = assess(pure_doc)

def summary_rows(rows, value_key, predicted_key):
    obs = np.asarray([float(r[value_key]) for r in rows])
    pred = np.asarray([float(r[predicted_key]) for r in rows])
    rel = 100 * (pred / obs - 1)
    return dict(n=len(rows), AARD_percent=float(np.mean(np.abs(rel))), signed_relative_bias_percent=float(np.mean(rel)))

pure_groups = {}
for group in dict.fromkeys(r['campaign'] for r in pure_assessment['rows']):
    these = [r for r in pure_assessment['rows'] if r['campaign'] == group]
    if these[0]['kind'] == 'pressure':
        role = 'fitted' if group in ('Klepacova2011', 'Belabbaci2010') else 'assessment_not_fitted'
        pure_groups[group] = dict(role=role, metric='vapor pressure', unit='percent', **summary_rows(these, 'observed', 'predicted'))
    else:
        pure_groups[group] = dict(role='fitted', metric='liquid density', unit='kg/m3', n=len(these),
                                  errors_kg_m3=[r['error_kg_m3'] for r in these])

binary_rows = list(csv.DictReader((AN / 'inputs/hartono-2013-table-3.csv').open()))
def eval_binary(label, doc):
    par = epcsaft.Parameters.from_mapping(doc)
    observations = [bubble(par, r, kind) for kind in 'Py' for r in binary_rows]
    calculated = predictions(par, observations)
    p_rows, y_rows = [], []
    for kind, source_rows in (('P', binary_rows), ('y', binary_rows)):
        dest = p_rows if kind == 'P' else y_rows
        for row, result in zip(source_rows, calculated[:26] if kind == 'P' else calculated[26:], strict=True):
            observed = 1000 * float(row['P_kPa']) if kind == 'P' else float(row['y_AMP'])
            dest.append(dict(row=row['row'], observed=observed, predicted=result['value'], status=result['status'], tolerance=result['tolerance']))
    for dest, kind in ((p_rows, 'total pressure'), (y_rows, 'vapor AMP mole fraction')):
        if any(x['status'] != 'Available' or x['tolerance'] is False for x in dest):
            raise RuntimeError(f'{label}: unavailable binary prediction in {kind}')
    return dict(parameters=doc, pressure=dict(role='fitted', metric='total pressure', unit='Pa', **summary_rows(p_rows, 'observed', 'predicted'), rows=p_rows),
                vapor_composition=dict(role='fitted', metric='vapor AMP mole fraction', unit='dimensionless', **summary_rows(y_rows, 'observed', 'predicted'), rows=y_rows))

old_doc = json.loads((AN / 'inputs/amp-document.json').read_text())
reported_doc = json.loads((AN / 'results/retransfer-344-05e94210/campaign/start-0/unpenalized/stage-0/parameters.json').read_text())['parameters']

hashes = {}
for rel in ('inputs/pure-amp.csv', 'inputs/amp-pure-endpoint.json', 'inputs/hartono-2013-table-3.csv', 'inputs/amp-document.json',
            'results/pure/summary.json', 'results/binary-dielectric.json',
            'results/retransfer-344-05e94210/campaign/start-0/unpenalized/stage-0/parameters.json'):
    hashes[rel] = hashlib.sha256((AN / rel).read_bytes()).hexdigest()

results = dict(
    engine=dict(identity='main-05e94210', wheel_sha256='c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb'),
    pure=dict(parameter_values=json.loads((AN / 'results/pure/summary.json').read_text())['frozen_endpoint']['values'],
              groups=pure_groups, rows=pure_assessment['rows'], unavailable=pure_assessment['unavailable']),
    binary={
        'earlier_binary_fit': eval_binary('earlier_binary_fit', old_doc),
        'reported_part_ii_fit_start_0_unpenalized': eval_binary('reported_part_ii_fit_start_0_unpenalized', reported_doc),
    },
    input_sha256=hashes,
)
results['runtime_seconds'] = time.perf_counter() - started
OUT.write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')
print(json.dumps(dict(output=str(OUT), runtime_seconds=results['runtime_seconds'], pure_groups=pure_groups,
                      binary={k: {g: {m: x[g][m] for m in ('n','AARD_percent','signed_relative_bias_percent')} for g in ('pressure','vapor_composition')} for k,x in results['binary'].items()}), indent=2))
