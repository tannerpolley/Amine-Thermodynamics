"""Issue 255 stage 3: downstream evidence for the selected stability-constrained candidate; no adoption.

Reruns the producers the paper and notebook read, on the final set and on the candidate, both on the bc779473 wheel:
the selected-assessment producer (paper point data), the model curves, the Kim 2007 heat pathways, the #268 density
comparison, the #264 heat-capacity comparison and the #267 MDEA transfer. Retained producers are copied with path, record
and hash substitutions only (copies kept under evidence/<name>/producers/). Outputs: results/stable-refit-255/evidence/.
Command (repository root, worktree .venv, background `agent-heavy`): final | all | compare | present
"""
# ruff: noqa: E402 -- numerical-library threads and the wheel identity are set before Engine imports.
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent))
import stable_refit_255 as r

d, s = r.d, r.s
ROOT, B = r.ROOT, r.B
RES = B / 'results'
EV = r.OUT / 'evidence'
A7 = RES / 'joint-recalibration-170/amendment-7/selected-assessment'
SPEC = RES / 'engine-3e83e19c-refit-chain/restricted-2/attempt-3/spec.json'
SCRIPTS = B / 'scripts'
RECORDS = {'final': RES / 'selected-current-best-parameters.json', 'candidate': EV / 'candidate-parameters.json'}
MODES = ('inventory', 'cp', 'density', 'declared-density', 'calorics', 'carbonate', 'states')
# Runs a substituted producer copy as __main__ after binding the authorized wheel and the evaluated record.
BOOT = '''
import importlib.machinery, importlib.util, json, os, pathlib, sys
cfg = json.loads(os.environ['EVIDENCE_255'])
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
sys.path[:0] = cfg['path']
import shared_evaluation as s
s.ENGINE_COMMIT = cfg['commit']
# The installed bytes are checked against this authorized wheel; older producers that assign their own retired pin
# (accept_engine_delivery.py) must not replace it.
s.ENGINE_WHEEL_SHA256 = cfg['sha']  # module global read by verify_wheel; the class property below ignores later assignments
s.__class__ = type('AuthorizedWheel', (type(s),), {'ENGINE_WHEEL_SHA256': property(lambda self: cfg['sha'], lambda self, value: None)})
if cfg['record']:
    s.PARAMETERS = pathlib.Path(cfg['record'])
for name, path in cfg['modules'].items():
    spec = importlib.util.spec_from_loader(name, importlib.machinery.SourceFileLoader(name, path))
    sys.modules[name] = module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
sys.argv = [cfg['copy'], *cfg['argv']]
exec(compile(open(cfg['copy']).read(), cfg['copy'], 'exec'))
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rows(path):
    with Path(path).open() as stream:
        return list(csv.DictReader(stream))


def table(path, values):
    with Path(path).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(dict.fromkeys(k for v in values for k in v)), lineterminator='\n')
        writer.writeheader()
        writer.writerows(values)


def copy_of(name, source, subs, truncate=None):
    text = source.read_text()
    if truncate:
        text = text[:text.index(truncate)]
    text = text.replace('Path(__file__)', f'Path({str(source)!r})')  # the copy keeps its source's location
    for old, new in subs:
        assert old in text, (source.name, old)
        text = text.replace(old, new)
    path = EV / name / 'producers' / (source.name.removesuffix('.txt') + '.txt')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def run(name, path, argv, record=True, modules=None):
    cfg = dict(path=[str(SCRIPTS), str(B / 'calibration-misfit'), str(ROOT / 'src')], sha=r.SHA, commit=r.COMMIT,
               record=str(RECORDS[name]) if record else None, modules=modules or {}, copy=str(path), argv=list(argv))
    print('run', name, path.name, *argv, flush=True)
    subprocess.run([sys.executable, '-u', '-c', BOOT], cwd=ROOT, check=True, env=dict(os.environ, EVIDENCE_255=json.dumps(cfg)))


def document():
    chosen = r.result('primary.json')
    assert chosen['outcome'] == 'A', 'no stable candidate passed; there is no downstream rerun'
    EV.mkdir(parents=True, exist_ok=True)
    if not RECORDS['candidate'].exists():
        RECORDS['candidate'].write_text(json.dumps(r.result(f"{chosen['run']}/candidate.json"), indent=2, allow_nan=False) + '\n')
    return chosen['run']


def assessment(name):
    out = EV / name / 'selected-assessment'
    out.mkdir(parents=True, exist_ok=True)
    common = [("Path('analyses/mea_parameter_bundle/results/engine-3e83e19c-paper-evidence/selected-assessment').resolve()",
               f'Path({str(out)!r})'), ('OUT.parents[1]', f'Path({str(RES)!r})')]
    if not (out / 'states-complete.json').exists():
        producer = copy_of(name, A7 / 'assess.py.txt', [*common,
            ("RECORD = BASE/'run/fit/usable-budget-endpoint.json'", f'RECORD = Path({str(RECORDS[name])!r})'),
            ("'00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'", repr(sha(RECORDS[name]))),
            ("OUT.parent/'assessments-timing.json',", ''), (",OUT.parent/'gate-verification.json'", '')])
        for mode in MODES:
            if mode == 'inventory' or not (out / f'{mode}-complete.json').exists():
                run(name, producer, [mode])
    if not (out / 'summary.json').exists():
        # The retained reduction up to its fit-identity checks, which bind the #212 fit files and do not apply here.
        producer = copy_of(name, A7 / 'reduce.py.txt', common, truncate='# Numerical checks against this exact vector')
        with producer.open('a') as stream:
            stream.write("write('summary.json',dict(parameter_sha256=load('provenance.json')['parameter_sha256'],"
                         "engine_wheel_sha256=load('provenance.json')['engine_wheel_sha256'],density=denscores,Cp=cpstats,"
                         "heat=heatstats,state=load('state-summary.json'),carbonate=carbon_scores))\n")
        run(name, producer, [])


def point_data(name, run_name):
    """reduce_a7_evidence's point-data split of the retained assessment, for the files the paper and curves read."""
    out, assessed = EV / name, EV / name / 'selected-assessment'
    for file in ('state-targets.csv', 'state-summary.json', 'states-excluded.json', 'states-unavailable.json', 'summary.json',
                 'density.csv', 'cp.csv', 'carbonate-share.csv'):
        shutil.copyfile(assessed / file, out / file)
    states, digest = rows(assessed / 'state-targets.csv'), sha(RECORDS[name])
    assert all(x['status'] == 'Available' and x['record_sha256'] == digest for x in states)
    counts = {}
    for file, kind, quantity in [('pressure-figure-data.csv', 'packet', 'pressure'), ('species-figure-data.csv', 'packet', 'species'),
                                 ('canonical-pressure.csv', 'canonical', 'pressure'), ('wagner-pressure.csv', 'wagner', 'pressure'),
                                 ('transfer.csv', 'transfer', 'pressure')]:
        chosen = [x for x in states if (x['kind'], x['quantity']) == (kind, quantity)]
        counts[file] = len(chosen)
        table(out / file, chosen)
    table(out / 'pool-figure-data.csv', [x for x in states if x['kind'] == 'packet' and x['source'] == 'Matin2012' and x['species'] == 'HCO3-'])
    scores = json.loads((assessed / 'state-summary.json').read_text())['scores']
    table(out / 'high-temperature-comparison.csv', [dict(cohort=k, **{f: v for f, v in c.items() if f not in ('row_ids', 'state_ids')})
                                                    for k, c in scores.items() if '100-120' in k])
    replay = r.result('qualification/final-replay.json' if name == 'final' else f'{run_name}/replay.json')
    fitted = {v['identity'] for v in replay}
    sources = {x['record_id']: x for x in json.loads((ROOT / json.loads(SPEC.read_text())['heat_rows_path']).read_text())}
    table(out / 'heat.csv', [dict(x, scale_J_mol_CO2=sources[x['id']]['uH_J_per_mol_CO2'], unit='kJ/mol CO2',
                                  role='fitted' if x['id'] in fitted else 'non-fitted prediction', source_row=sources[x['id']])
                             for x in rows(assessed / 'heats.csv')])
    table(out / 'fitted-rows.csv', [dict(id=v['identity'], group=v['group'], quantity=v['row'].get('quantity') or v['row'].get('kind'),
                                         observed=v['observed'], predicted=v['value'], residual=v['residual'], weighted_residual=v['weighted_residual'],
                                         cost=v['cost'], status=v['status']) for v in replay])
    (out / 'point-counts.json').write_text(json.dumps(dict(counts, state_targets=len(states), fitted_rows=len(replay)), indent=2) + '\n')


def curves(name):
    return copy_of(name, SCRIPTS / 'model_curves.py', [
        ("BUNDLE / 'results/engine-3e83e19c-paper-evidence'", f'Path({str(EV / name)!r})'),
        ("BUNDLE / 'results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json'", f'Path({str(RECORDS[name])!r})')])


def kim(name, model_curves):
    if (EV / name / 'kim2007-heat-pathways').exists():
        return
    producer = copy_of(name, SCRIPTS / 'kim2007_heat_pathways.py', [
        ("BUNDLE / 'results/kim2007-heat-pathways-245'", f"Path({str(EV / name / 'kim2007-heat-pathways')!r})"),
        ("BUNDLE / 'figures/kim2007-heat-pathways-245'", f"Path({str(EV / name / 'kim2007-heat-pathways-figures')!r})"),
        ("BUNDLE / 'results/engine-3e83e19c-paper-evidence'", f'Path({str(EV / name)!r})'),
        ("'00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91'", repr(sha(RECORDS[name]))),
        ("c.RECORD.parents[2]/'spec.json'", f'Path({str(SPEC)!r})')])
    for step in ('calculate', 'present'):
        run(name, producer, [step], modules={'model_curves': str(model_curves)})


def density(name):
    """#268's 234-row comparison (paper-evidence density inputs plus Sobrino 2016) at the record."""
    path = EV / name / 'density-268.json'
    if path.exists():
        return
    d.OUT, d.SHA = EV / name, r.SHA
    _, records, values = d.comparisons('density-268', s.parameter_mapping(RECORDS[name]))
    groups = {}
    for record, value in zip(records, values, strict=True):
        row = record['row']
        key = (row['source'], float(row['loading']) > 0, float(row['T_K']) > 353.15 + 1e-9)
        groups.setdefault(key, []).append((row, value))
    summary = []
    for (source, loaded, hot), members in sorted(groups.items()):
        ok = [(x, v) for x, v in members if v['status'] == 'Available']
        errors = [v['error_kg_m3'] for _, v in ok]
        expanded = [(x, v) for x, v in ok if x.get('source_expanded_uncertainty_value')]
        summary.append(dict(source=source, loaded=loaded, above_353_K=hot, n=len(members), available=len(ok),
                            mean_error_kg_m3=sum(errors) / len(ok), RMSE_kg_m3=math.sqrt(sum(e * e for e in errors) / len(ok)),
                            AARD_percent=sum(abs(v['error_percent']) for _, v in ok) / len(ok),
                            within_2s=sum(abs(v['residual']) <= 2 for _, v in ok), source_expanded_available=len(expanded),
                            within_source_expanded=sum(abs(v['error_kg_m3']) <= float(x['source_expanded_uncertainty_value']) for x, v in expanded)))
    path.write_text(json.dumps(dict(wheel_sha256=r.SHA, parameter_sha256=sha(RECORDS[name]), groups=summary), indent=1, allow_nan=False) + '\n')


def heat_capacity(name):
    """#264's 60 broad Cp rows (corrected water record), evaluated at the record's parameters and reaction laws."""
    path = EV / name / 'heat-capacity-264.json'
    if path.exists():
        return
    sys.path.insert(0, str(B / 'heat-capacity-264'))
    import calculate as hc
    mapping = s.parameter_mapping(RECORDS[name])
    hc.SolventSpecification = lambda toml: d.bind(mapping)
    spec, _, broad, _ = hc.setup()
    predictions = hc.evaluate(spec, broad)
    assert hc.available(predictions)
    rows_out = [dict(identity=x['identity'], group=x['group'], source=x['row']['source'], T_K=float(x['row']['T_K']), loading=float(x['row']['loading']),
                     observed_kJ_kg_K=float(x['row']['cp_kJ_kg_K']), predicted_kJ_kg_K=p['value'] * x['feed_amount_mol'] / x['feed_mass_kg'] / 1000,
                     residual=p['residual']) for x, p in zip(broad, predictions, strict=True)]
    for x in rows_out:
        x['error_percent'] = 100 * (x['predicted_kJ_kg_K'] / x['observed_kJ_kg_K'] - 1)
    path.write_text(json.dumps(dict(wheel_sha256=r.SHA, parameter_sha256=sha(RECORDS[name]), metrics=r.jsonable(hc.group_metrics(broad, predictions)), rows=rows_out), indent=1, allow_nan=False) + '\n')


def mdea(k):
    """#267's MDEA pressure and heat checks with the shared bicarbonate-water k at the final-set and candidate values."""
    out = EV / 'mdea-transfer'
    if (out / 'heat.json').exists():
        return
    source = ROOT / 'analyses/mdea_mea_workflow/scripts/transfer_probes.py'
    old_wheel = "'/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-d5138209/epcsaft-1.0.0-cp313-cp313-manylinux_2_39_x86_64.whl'"
    producer = copy_of('candidate', source, [
        ("AN / 'results/transfer-267'", f'Path({str(out)!r})'), (old_wheel, repr(str(r.WHEEL))),
        ("'ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5'", repr(r.SHA)),
        ("for suffix,k in [('',base_k),('-kminus',base_k-.1),('-kplus',base_k+.1)]:", f"for suffix,k in [('-final-k',base_k),('-candidate-k',{k!r})]:"),
        ("            assess(read(AN/f'results/stage2-capped/{label}/followup-bicarbonate/endpoint.json'),label+'-released')\n", ''),
        ("for label,T in [('B1',333.15),('A3',333.15),('B1',388.71)]:", f"for (label,T),kk in [(c,kk) for c in [('B1',333.15),('A3',333.15),('B1',388.71)] for kk in (base_k,{k!r})]:"),
        ("            s.setup(read(AN/f'results/stage2-capped/{label}/endpoint.json'))\n",
         "            document=read(AN/f'results/stage2-capped/{label}/endpoint.json'); pair(document)['value']['magnitude']=kk; s.setup(document)\n"),
        ("results.append(dict(label=label,T_K=T,", "results.append(dict(label=label,k=kk,T_K=T,")])
    for mode in ('pressure', 'heat'):
        run('candidate', producer, [mode], record=False)


def compare():
    """Same-wheel, same-input differences between the candidate and the final set for every rerun output."""
    out = []

    def add(domain, cohort, metric, final, candidate):
        change = candidate - final if isinstance(final, (int, float)) and isinstance(candidate, (int, float)) else None
        out.append(dict(domain=domain, cohort=cohort, metric=metric, final=final, candidate=candidate, change=change))

    load = lambda name, file: json.loads((EV / name / file).read_text())
    chosen = r.result('primary.json')['run']
    assessed = r.result(f'{chosen}/assessment.json')
    for group, m in assessed['metrics'].items():
        for key in ('n', 'within_2s', 'aard_percent', 'rmse', 'cost'):
            add('307 objective rows', group, key, assessed['baseline_metrics'][group][key], m[key])
    f, c = load('final', 'summary.json'), load('candidate', 'summary.json')
    for cohort, score in f['state']['scores'].items():
        for key in ('n_available', 'AARD_percent', 'bias', 'mean_ln_calc_over_obs'):
            add('paper states', cohort, key, score.get(key), c['state']['scores'][cohort].get(key))
    for cohort, score in f['density'].items():
        for key in ('n_available', 'RMSE', 'AARD_percent', 'within_2s'):
            add('paper density', cohort, key, score.get(key), c['density'][cohort].get(key))
    for cohort, score in f['heat'].items():
        for key in ('n_available', 'RMSE', 'AARD_percent', 'bias'):
            add('paper heat', cohort, key, score.get(key), c['heat'][cohort].get(key))
    for row, other in zip(f['Cp'], c['Cp'], strict=True):
        add('paper heat capacity', row['id'], 'error_percent', row['error_percent'], other['error_percent'])
    for cohort, score in f['carbonate'].items():
        for key in ('calc_over_obs_min', 'calc_over_obs_max', 'mean_calc_over_obs'):
            add('paper carbonate share', cohort, key, score.get(key), c['carbonate'][cohort].get(key))
    for family in ('pressure', 'species', 'heat', 'density', 'mea-water'):
        a, b = rows(EV / 'final/model-curves' / f'{family}.csv'), rows(EV / 'candidate/model-curves' / f'{family}.csv')
        # State inputs only: the pressure family solves for pressure and the MEA-water family for temperature.
        inputs = ('curve', 'analytical_loading', 'mea_mass_fraction', 'liquid_mea_mole_fraction', 'quantity') + \
            (() if family == 'pressure' else ('pressure_Pa',)) + (() if family == 'mea-water' else ('temperature_K',))
        key = lambda x: tuple(x[k] for k in inputs if k in x)
        # Grid states only (adaptive midpoints differ between records); rows are written in completion order.
        other = {key(y): y for y in b if y['sampling'] == 'grid'}
        grid = [x for x in a if x['sampling'] == 'grid']
        assert len(other) == len(grid) and all(key(x) in other for x in grid), family
        both = [(x, other[key(x)]) for x in grid]
        both = [(x, y) for x, y in both if x['status'] == y['status'] == 'available' and x['value'] and y['value']]
        add('model curves', family, 'available', sum(x['status'] == 'available' for x in a), sum(y['status'] == 'available' for y in b))
        for quantity in dict.fromkeys(x['quantity'] for x, _ in both):
            pairs = [(float(x['value']), float(y['value'])) for x, y in both if x['quantity'] == quantity]
            floor = 1e-4 * max(abs(u) for u, _ in pairs)  # relative change only where the value is resolved on its own scale
            add('model curves', f'{family}: {quantity}', 'max_absolute_change', 0., max(abs(v - u) for u, v in pairs))
            add('model curves', f'{family}: {quantity}', 'max_relative_change_above_1e-4_of_max', 0., max(abs(v / u - 1) for u, v in pairs if abs(u) >= floor))
    for name in ('final', 'candidate'):
        s_ = load(name, 'model-curves/summary.json')
        assert all(x['passed'] for x in s_['check_1_reference_replay']), name
    f, c = load('final', 'kim2007-heat-pathways/summary.json'), load('candidate', 'kim2007-heat-pathways/summary.json')
    for kind, score in f['pooled_313_353'].items():
        for key in ('n', 'rmse', 'bias', 'aard_percent'):
            add('Kim 2007 pooled 313-353 K', kind, key, score.get(key), c['pooled_313_353'][kind].get(key))
    f, c = load('final', 'density-268.json')['groups'], load('candidate', 'density-268.json')['groups']
    for x, y in zip(f, c, strict=True):
        cohort = f"{x['source']} {'loaded' if x['loaded'] else 'CO2-free'} {'above' if x['above_353_K'] else 'to'} 353 K"
        for key in ('available', 'mean_error_kg_m3', 'RMSE_kg_m3', 'AARD_percent', 'within_source_expanded'):
            add('density 234 rows (#268)', cohort, key, x[key], y[key])
    f, c = load('final', 'heat-capacity-264.json'), load('candidate', 'heat-capacity-264.json')
    for group, m in f['metrics']['groups'].items():
        other = c['metrics']['groups'][group]
        add('heat capacity 60 rows (#264)', group, 'AARD_percent', m['AARD_percent'], other['AARD_percent'])
        add('heat capacity 60 rows (#264)', group, 'within_2scale', len(m['within_2scale']), len(other['within_2scale']))
    for T in sorted({x['T_K'] for x in f['rows']}):
        pick = lambda doc: [x['error_percent'] for x in doc['rows'] if x['T_K'] == T]
        add('heat capacity 60 rows (#264)', f'{T} K', 'mean_error_percent', sum(pick(f)) / len(pick(f)), sum(pick(c)) / len(pick(c)))
    for label in ('A3', 'B1'):
        f, c = (load('candidate', f'../mdea-transfer/{label}-{k}/summary.json') for k in ('final-k', 'candidate-k'))
        for source in ('Xiao', 'Ermatchkov'):
            for key in ('available', 'AARD_percent', 'bias_percent'):
                add('MDEA transfer pressure', f'{label} {source}', key, f['pressure'][source][key], c['pressure'][source][key])
    heat = json.loads((EV / 'mdea-transfer/heat.json').read_text())
    for x in heat:
        if x['k'] != heat[0]['k'] and len(x['grid']) == 30:
            base = next(y for y in heat if (y['label'], y['T_K'], len(y['grid'])) == (x['label'], x['T_K'], 30) and y['k'] == heat[0]['k'])
            add('MDEA transfer heat (30-point grid)', f"{x['label']} {x['T_K']} K", 'value_J_mol_or_status',
                base['value'] if base['status'] == 'Available' else base['status'], x['value'] if x['status'] == 'Available' else x['status'])
    table(EV / 'comparison.csv', out)
    print(len(out), 'comparison rows', flush=True)


def present():
    """Presentation only, from retained outputs: pressure curves with 30 wt% canonical observations, and loaded-density errors."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    canonical = {'canonical:' + x['observation_id']: x for x in rows(ROOT / 'data/reference/MEA/observations/vapor_liquid_equilibrium/Canonical_VLE_Observations.csv')}
    plotted, colors = [], dict(zip((313.15, 353.15, 393.15), ('#0072B2', '#E69F00', '#D55E00')))
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.4))
    for T, color in colors.items():
        for name, style in (('final', '--'), ('candidate', '-')):
            curve = sorted((float(x['analytical_loading']), float(x['value'])) for x in rows(EV / name / 'model-curves/pressure.csv')
                           if x['status'] == 'available' and x['sampling'] == 'grid' and float(x['temperature_K']) == T)
            left.plot(*zip(*curve), style, color=color, lw=1.4, label=f'{T:g} K, {name}')
            plotted += [dict(panel='pressure', series=f'{name} curve', T_K=T, loading=a, value_Pa=v) for a, v in curve]
        points = [(float(x['loading']), float(x['observed'])) for x in rows(EV / 'candidate/canonical-pressure.csv')
                  if abs(float(x['temperature_K']) - T) < 3 and abs(float(canonical[x['identity']]['MEA_weight_fraction']) - .3) < .005]
        if points:
            left.plot(*zip(*points), 'o', mfc='none', color=color, ms=5)
            plotted += [dict(panel='pressure', series='canonical observation, 30 wt%, within 3 K', T_K=T, loading=a, value_Pa=v) for a, v in points]
    left.set(yscale='log', xlabel='CO$_2$ loading / mol mol$^{-1}$ MEA', ylabel='CO$_2$ partial pressure / Pa', title='30 wt% MEA: curves move by at most 7%')
    left.legend(fontsize=7, ncol=2)
    for name, marker in (('final', 'o'), ('candidate', 'x')):
        values = json.loads((EV / name / 'density-268/density.json').read_text())['result']
        source = {x['id']: x for x in d.density_rows()}
        points = [(float(source[v['identity']]['T_K']), v['error_kg_m3'], source[v['identity']]['source']) for v in values
                  if v['status'] == 'Available' and float(source[v['identity']]['loading']) > 0]
        right.plot([x for x, _, _ in points], [y for _, y, _ in points], marker, mfc='none', ms=4, color='#333333' if name == 'final' else '#CC79A7', label=name)
        plotted += [dict(panel='loaded density', series=name, T_K=x, error_kg_m3=y, source=z) for x, y, z in points]
    right.axhline(0, color='0.6', lw=.8)
    right.axvline(353.15, color='0.6', lw=.8, ls=':')
    right.set(xlabel='Temperature / K', ylabel='Model minus measured density / kg m$^{-3}$', title='Loaded density: smaller bias above 353 K;\nHan α = 0.56 rows rise by about 10 kg m$^{-3}$')
    right.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(EV / 'candidate-comparison.png', dpi=180)
    table(EV / 'candidate-comparison-plotted-values.csv', plotted)


def everything(names=('final', 'candidate')):
    r.verify()
    run_name = document() if 'candidate' in names else None
    for name in names:
        assessment(name)
        point_data(name, run_name)
        model_curves = curves(name)
        if not (EV / name / 'model-curves/summary.json').exists():
            run(name, model_curves, [])
        kim(name, model_curves)
        density(name)
        heat_capacity(name)
    if 'candidate' in names:
        mdea(next(c['value']['magnitude'] for p in s.parameter_mapping(RECORDS['candidate'])['pairs']
                  if {p['component_id_a'], p['component_id_b']} == {'water', 'bicarbonate-anion'} for c in p['coefficients'] if c['family'] == 'k_ij'))


if __name__ == '__main__':
    {'all': everything, 'final': lambda: everything(('final',)), 'compare': compare, 'present': present}[sys.argv[1]]()
