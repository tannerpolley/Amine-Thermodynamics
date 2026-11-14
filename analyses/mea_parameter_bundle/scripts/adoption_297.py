"""Fixed-parameter qualification for #297; defaults change only after F1–F3."""
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).parent))
import stable_refit_255 as r

BASE = 'e165b828624e7ddd41f3011142936fc524a51455'
ACCEPTED = 'e9009a8'
COMMIT = '391dfe5d64ede5036bf160bc6ae037ad5e14af32'
SHA = '0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b'
OLD = r.OUT
OUT = r.B / 'results/adoption-297'
WHEEL = r.ROOT / f'build/engine-wheels/main-{COMMIT}/epcsaft-1.3.0-cp313-cp313-manylinux_2_39_x86_64.whl'
r.SHA, r.COMMIT, r.WHEEL = SHA, COMMIT, WHEEL
r.s.ENGINE_WHEEL_SHA256, r.s.ENGINE_COMMIT = SHA, COMMIT
RECORDS = {'incumbent': r.CHAIN / 'restricted-2/attempt-3/run/fit/usable-budget-endpoint.json',
           'candidate': OLD / 'evidence/candidate-parameters.json'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(name, value):
    r.s.write_json(OUT / name, value)


def relative(a, b):
    return abs(a-b) / max(abs(a), abs(b), 1e-300)


def verify():
    r.verify()
    assert r.s.installed_wheel().resolve() == WHEEL.resolve()
    subprocess.check_output(['git', '-C', str(r.ROOT / 'upstream/ePC-SAFT'), 'merge-base', '--is-ancestor', COMMIT, 'origin/main'])
    with zipfile.ZipFile(WHEEL) as z:
        files = {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()
                 if n.startswith(('epcsaft/', 'epcsaft.libs/')) and not n.endswith('/')}
        base = Path(r.epcsaft.__file__).parent.parent
        assert all(sha(base / n) == h for n, h in files.items())
    write('wheel.json', dict(commit=COMMIT, sha256=SHA, path=str(WHEEL), modules=files,
          direct_url=json.loads(importlib.metadata.distribution('epcsaft').read_text('direct_url.json')),
          implementation_base=BASE, accepted_inputs_commit=ACCEPTED))


def f1():
    verify()
    # Byte identity against the accepted study covers every input field, including roles,
    # physical templates, row scales/weights, reaction references and the #260 caloric record.
    paths = [] if CONFIG else subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', ACCEPTED,
        'analyses/solvent_specification_mea', 'analyses/mea_parameter_bundle/data/input',
        'src/MEA/common/mea_source_contracts.py'], cwd=r.ROOT, text=True).splitlines()
    inventory = []
    for name in paths:
        path = r.ROOT / name
        old = subprocess.check_output(['git', 'show', f'{ACCEPTED}:{name}'], cwd=r.ROOT)
        inventory.append(dict(path=name, sha256=sha(path), identical=old == path.read_bytes()))
    if CONFIG:
        inventory = [dict(path=name, sha256=sha(r.ROOT/name), identical=sha(r.ROOT/name)==digest)
                     for name, digest in CONFIG['input_sha256'].items()]
    write('input-identity.json', inventory)
    assert all(x['identical'] for x in inventory), 'F1: frozen physical input changed'
    summary = {}
    for name, path in RECORDS.items():
        ref = (r.read(r.ROOT / CONFIG['references'][name])['rows'] if CONFIG else
               r.read(OLD / ('qualification/final-replay.json' if name == 'incumbent' else 'wide/replay.json'))['result'])
        values, ok, cost = r.replay(r.s.parameter_mapping(path))
        write(f'{name}/replay.json', dict(wheel_sha256=SHA, engine_commit=COMMIT, parameter_sha256=sha(path), rows=values, cost=cost))
        declarations = [{k: x[k] for k in ('identity', 'group', 'observed', 'row')} for x in values]
        exact = declarations == [{k: x[k] for k in ('identity', 'group', 'observed', 'row')} for x in ref]
        differences = [relative(v['value'], b['value']) for v, b in zip(values, ref, strict=True)] if ok else []
        refcost = math.fsum(x['cost'] for x in ref)
        summary[name] = dict(rows=len(values), available=ok, declarations_identical=exact, cost=cost,
            reference_cost=refcost, relative_cost_difference=relative(cost, refcost) if ok else None,
            largest_relative_prediction_difference=max(differences, default=None),
            passed=ok and exact and len(values)==307 and max(differences)<=1e-10 and relative(cost,refcost)<=1e-10)
        write('f1.json', summary)
        print(name, summary[name], flush=True)
    assert all(x['passed'] for x in summary.values()), 'F1 failed: computation or inputs do not reproduce selected evidence'


def f2():
    if CONFIG:
        import reduced_refit_338 as reduced
        reduced.OUT = OUT
        reduced.split_registry = lambda: r.read(r.ROOT / CONFIG['registry'])
        result = reduced.search('candidate', r.s.parameter_mapping(RECORDS['candidate']))
        reference = r.read(r.ROOT / CONFIG['search_reference'])
        fields = {'grid': ('states', 'available', 'descent'), 'offset': ('states', 'available', 'descent'),
                  'census': ('states', 'descent', 'incomplete'),
                  'supplied': ('compositions', 'evaluated', 'negative', 'unavailable')}
        assert all(result[g][k] == reference[g][k] for g, keys in fields.items() for k in keys)
        write('f2.json', dict(result=result, passed=True))
        return
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import phase_diagnosis_255 as p
    verify()
    assert all(x['passed'] for x in r.read(OUT / 'f1.json').values())
    enforced, offset = r.states()
    excluded = set(r.read(OLD / 'qualification/summary.json')['result']['excluded'])
    census = r.read(r.B / 'results/engine-3e83e19c-phase-search/run-2/inputs/states.json')
    summaries = {}
    for name, path in RECORDS.items():
        mapping = r.s.parameter_mapping(path)
        directory = OUT / name / 'stability'
        directory.mkdir(parents=True, exist_ok=True)
        chosen = enforced + offset
        with ProcessPoolExecutor(int(os.environ['AGENT_HEAVY_CORES']), initializer=r._init, initargs=(mapping,)) as pool:
            jobs = {pool.submit(r._measure, state): (i, state) for i, state in enumerate(chosen)
                    if not (directory / f'{i:04d}.json').exists()}
            for job in as_completed(jobs):
                i, state = jobs[job]
                row = job.result()
                write(f'{name}/stability/{i:04d}.json', row)
                print(name, i, row['key'], row['available'], row.get('value'), flush=True)
        rows = [r.read(directory / f'{i:04d}.json') for i in range(len(chosen))]
        checks = dict(enforced=r.tally([x for x in rows[:1908] if x['key'] not in excluded]),
                      excluded=r.tally([x for x in rows[:1908] if x['key'] in excluded]), offset=r.tally(rows[1908:]))
        directory = OUT / name / 'census'
        directory.mkdir(exist_ok=True)
        with ProcessPoolExecutor(int(os.environ['AGENT_HEAVY_CORES']), initializer=verify) as pool:
            jobs = {pool.submit(r._census, (mapping, state, directory / f"tmp-{state['index']}.json")): state['index']
                    for state in census if not (directory / f"{state['index']}.json").exists()}
            for job in as_completed(jobs):
                index = jobs[job]
                raw, reduced = job.result()
                write(f'{name}/census/{index}.json', dict(raw=raw, reduced=reduced))
                print(name, 'census', index, reduced, flush=True)
        reduced = [r.read(directory / f"{state['index']}.json")['reduced'] for state in census]
        checks['census'] = dict(states=len(reduced), available=sum(x['complete'] for x in reduced),
                               descent=sum(x['resolved'] > 0 for x in reduced))
        summaries[name] = checks
        write('f2.json', summaries)
    candidate = summaries['candidate']
    passed = (candidate['enforced']['available'] == 1903 and candidate['offset']['available'] == 576
              and candidate['census']['available'] == 162 and all(x['descent']==0 for x in candidate.values()))
    write('f2.json', dict(records=summaries, passed=passed))
    assert passed, 'F2 failed: descent, unavailable enforced state, or lost check availability'


def f3():
    values = {name: r.read(OUT / name / 'replay.json') for name in RECORDS}
    metrics = {name: r.metrics(x['rows']) for name, x in values.items()}
    checks = r.acceptance(metrics['candidate'], metrics['incumbent'])
    threshold = values['incumbent']['cost'] * (1-1e-6)
    cai = {}
    for name, replay in values.items():
        cai[name] = {}
        for quantity, unit in [('temperature', 'K'), ('mole_fraction', '1')]:
            rows = [x for x in replay['rows'] if x['group']=='Cai' and x['row'].get('quantity')==quantity]
            if rows:
                cai[name][quantity] = dict(n=len(rows), unit=unit,
                    rmse=math.sqrt(math.fsum((x['value']-x['observed'])**2 for x in rows)/len(rows)))
    write('cai-units.json', cai)
    write('f3.json', dict(metrics=metrics, checks=checks, cost_limit=threshold,
          observation_cost=values['candidate']['cost'],
          passed=all(x['passed'] for x in checks.values()) and values['candidate']['cost'] < threshold))


def shared_values():
    import candidate_evidence_255 as e
    mapping = r.s.parameter_mapping(RECORDS['candidate'])
    pair = next(x for x in mapping['pairs'] if {x['component_id_a'],x['component_id_b']} == {'water','bicarbonate-anion'})
    law = e.r2_law(mapping)
    write('shared-bicarbonate-water.json', pair)
    write('shared-R2.json', law)
    write('shared-hashes.json', {name: sha(OUT/name) for name in ('shared-bicarbonate-water.json','shared-R2.json')})


def uncertainty():
    from types import SimpleNamespace
    import numpy as np
    import refit
    mapping = r.s.parameter_mapping(RECORDS['candidate'])
    spec = r.bind(mapping)
    shifts = r.read(OLD / 'wide/retreat.json')['result']['shifts']
    declared = r.coordinates(spec, shifts)
    physical = r.s.parameter_values(mapping)
    for q in declared:
        if 'targets' in q:
            q['origin'] = physical[q['identity']]
    spec.inputs['coordinates'] = declared
    qvalues = [q['origin'] for q in declared]
    lower, upper = [q['bounds'][0] for q in declared], [q['bounds'][1] for q in declared]
    scales = np.array([q['scale'] for q in declared])
    active = [i for i, v in enumerate(qvalues) if min(v-lower[i], upper[i]-v) <= 1e-6*scales[i]]
    ids = [q['identity'] for q in declared]
    result = dict(coordinate_map=declared, active_bounds=[ids[i] for i in active], wheel_sha256=SHA,
                  parameter_sha256=sha(RECORDS['candidate']))
    try:
        rows = spec.inputs['observations']['fitted']
        ev = r.reg.differentiate(spec.parameters, spec.coordinates(), [spec.observation(x) for x in rows],
                                optimizer=[0.]*len(declared), holds=[], thermochemistry=spec.thermal)
        reference = r.read(OUT/'candidate/replay.json')['rows']
        difference = max(relative(p,x['value']) for p,x in zip(ev.predictions,reference,strict=True))
        assert difference <= 1e-10, difference
        result['prediction_difference'] = difference
        weights = np.sqrt([x['weight'] for x in rows])
        J = np.array(ev.residual_optimizer_gradient).reshape(len(rows), len(declared))*weights[:,None]/scales
        residual = np.array([x['residual'] for x in r.read(OUT/'candidate/replay.json')['rows']])*weights
        free = [i for i in range(len(ids)) if i not in active]
        singular = np.linalg.svd(J[:,free], compute_uv=False)
        rank = int(np.sum(singular > 1e-14*singular[0]))
        result.update(rank_relative_cutoff=1e-14, free_singular_values=singular.tolist())
        result.update(rank=rank, free_coordinates=[ids[i] for i in free])
        if rank < len(free):
            result.update(available=False, reason='Rank deficient free-coordinate observation Jacobian')
        else:
            result.update(refit.identifiability(SimpleNamespace(physical=qvalues, covariance=SimpleNamespace(active_bounds=active)),
                                               J,residual,ids,lower,upper), available=True)
        write('conditional-information.json', dict(predictions=list(ev.predictions), weighted_jacobian=J.tolist()))
    except r.epcsaft.ParameterError as exc:
        result.update(available=False, reason=str(exc))
    units = {c['identity']:c['value']['unit'] for component in mapping['components'] for c in component['coefficients']}
    units.update({c['identity']:c['value']['unit'] for pair in mapping['pairs'] for c in pair['coefficients']})
    for q in declared:
        q['value'],q['unit'] = q['origin'],units.get(q['identity'],'K' if q.get('kind')=='reaction_coordinate' else 'J/mol')
        if q.get('kind')=='reaction_enthalpy_shift':
            q['value'] += shifts[q['name']]
            q['bounds'] = [v+shifts[q['name']] for v in q['bounds']]
    result['coordinate_convention'] = 'Exact #255 native coordinates: reaction:R5:correlation:a_k labels the completed native b coefficient (K), not the unshifted source A; enthalpy shifts displayed as totals.'
    result.setdefault('conditional_standard_error', {})
    write('conditional-uncertainty.json', result)


def f5():
    import csv
    package = OUT/'paper-evidence'
    reference = OLD/'evidence/candidate'
    comparisons = []
    files = ['state-targets.csv','density.csv','cp.csv','heat.csv','carbonate-share.csv']
    files += ['model-curves/'+x+'.csv' for x in ('pressure','species','heat','density','mea-water')]
    files += ['kim2007-heat-pathways/'+x+'.csv' for x in ('kim-heat','heat-curves','pathway-fractions','bottinger-fractions')]
    for filename in files:
        load = lambda base: list(csv.DictReader((base/filename).open()))
        old,new = load(reference),load(package)
        if filename.startswith('model-curves/'):
            family = Path(filename).stem
            keys = ['curve','sampling','analytical_loading','mea_mass_fraction','liquid_mea_mole_fraction','quantity']
            keys += ([] if family=='pressure' else ['pressure_Pa']) + ([] if family=='mea-water' else ['temperature_K'])
            quantities = ['value']
        else:
            keys = ['identity','species'] if 'species' in old[0] and 'identity' in old[0] and 'target' not in old[0] else ['id'] if 'id' in old[0] else ['record_id'] if 'record_id' in old[0] else ['target','kind','identity'] if 'target' in old[0] else ['T_K','loading']
            quantities = [k for k in old[0] if k.startswith(('predicted','calculated','equilibrium_cp','frozen_cp')) or k in
                          ('differential','integral','integral_co2_predicted','integral_mea_predicted','differential_predicted','carbamate','bicarbonate','free')]
        key = lambda row: tuple((k,row[k]) for k in keys if k in row)
        a,b = {key(x):x for x in old},{key(x):x for x in new}
        assert len(a)==len(old) and len(b)==len(new) and a.keys()==b.keys(), ('F5 row identity',filename,len(a),len(b))
        for identity,x in a.items():
            y=b[identity]
            for k in x:
                if k in y and (k in ('status','requested_tolerance_met','available_for_interpretation','interval_status') or k.endswith('_available')):
                    assert x[k]==y[k],('F5 availability',filename,identity,k,x[k],y[k])
            for q in quantities:
                if x[q] in ('','None','nan'):
                    assert x[q]==y[q],(filename,identity,q)
                    continue
                u,v = float(x[q]),float(y[q])
                comparisons.append(dict(file=filename,identity=identity,quantity=q,reference=u,value=v,
                    absolute_difference=abs(u-v),relative_difference=relative(u,v),unit=x.get('unit') or {'state-targets.csv':('Pa' if x.get('quantity')=='pressure' else '1'), 'density.csv':'kg/m3', 'cp.csv':'kJ/(kg K)', 'heat.csv':'kJ/mol CO2', 'carbonate-share.csv':'1'}.get(filename,'1' if 'fractions' in filename else 'kJ/mol CO2')))
    for filename, field, quantity in [('density-268/density.json','result','value'),('heat-capacity-264.json','rows','predicted_kJ_kg_K')]:
        a,b = r.read(reference/filename)[field],r.read(package/filename)[field]
        assert len(a)==len(b)
        for x,y in zip(a,b,strict=True):
            assert x['identity']==y['identity']
            if 'status' in x:
                assert x['status']==y['status']
            comparisons.append(dict(file=filename,identity=x['identity'],quantity=quantity,reference=x[quantity],value=y[quantity],
                absolute_difference=abs(x[quantity]-y[quantity]),relative_difference=relative(x[quantity],y[quantity]),unit='kg/m3' if filename.startswith('density') else 'kJ/(kg K)'))
    write('f5-comparison.json',comparisons)
    largest=max(comparisons,key=lambda x:x['relative_difference'])
    write('f5.json',dict(quantities=len(comparisons),largest=largest,tolerance=1e-8,
          passed=all(x['relative_difference']<=1e-8 for x in comparisons)))
    assert all(x['relative_difference']<=1e-8 for x in comparisons),('F5 producer difference',largest)


def extras():
    import candidate_evidence_255 as e
    import mea_water_permittivity as perm
    import fit_observations as fo
    import shutil
    verify()
    package = OUT/'paper-evidence'
    perm.OUT = package/'permittivity'
    perm.FIT_STAGE = r.CHAIN/'stage5/run/rows.json'
    perm.main(RECORDS['candidate'])
    water = fo.water_assessment(r.read(r.B/'results/water-124/spec.json'), r.s.parameter_mapping(RECORDS['candidate']))
    write('paper-evidence/water-checks.json',water)
    assert len(water['rows'])==42 and all(x['evaluated'] and x['cp_verified'] for x in water['rows'])
    e.table(package/'water.csv',[{k:v for k,v in x.items() if k!='enthalpy_ladder'} for x in water['rows']])
    write('paper-evidence/water-summary.json',dict(parameter_sha256=sha(RECORDS['candidate']), engine_commit=COMMIT,
          wheel_sha256=SHA, metrics=water['metrics'],states=42))
    uncertainty()
    shutil.copyfile(OUT/'conditional-uncertainty.json',package/'conditional-uncertainty.json')
    info = r.read(OUT/'conditional-uncertainty.json')
    e.table(package/'conditional-standard-errors.csv',[dict(identity=k,standard_error=v) for k,v in info['conditional_standard_error'].items()]
            or [dict(available=False,reason=info['reason'])])
    e.table(package/'conditional-correlations.csv',[dict(left=a,right=b,correlation=info['conditional_correlation'][i][j])
            for i,a in enumerate(info.get('free_coordinates',[])) for j,b in enumerate(info.get('free_coordinates',[]))]
            if info['available'] else [dict(available=False,reason=info['reason'])])
    values = r.read(OUT/'candidate/replay.json')
    groups = {}
    for row in values['rows']:
        groups.setdefault(row['group'],[]).append(row)
    groups = {k:dict(n=len(v),cost=math.fsum(x['cost'] for x in v)) for k,v in groups.items()}
    write('paper-evidence/fit-summary.json',dict(cost=values['cost'],groups=groups,coordinates=info['coordinate_map'],
          active_bounds=[i for i,q in enumerate(info['coordinate_map']) if q['identity'] in info['active_bounds']],engine=dict(wheel_path=str(WHEEL.relative_to(r.ROOT)),wheel_sha256=SHA,commit=COMMIT),
          record_sha256=sha(RECORDS['candidate']), fitting='No optimization performed; fixed #255 candidate'))
    for name in ('density-scales.json','physical-ideal-gas-calorics.json','chemical_reaction_source_contract.json','density-source-differences.json'):
        destination=package/'source-only'/name
        destination.parent.mkdir(exist_ok=True)
        shutil.copyfile(r.B/'results/engine-3e83e19c-paper-evidence/source-only'/name,destination)


def phase_export():
    import csv
    import candidate_evidence_255 as e
    original = list(csv.DictReader((r.B/'results/engine-3e83e19c-paper-evidence/phase-family.csv').open()))
    rows = []
    for row in original:
        if row['record']=='reported':
            index = int(row['index'])
            state = r.read(OUT/f'candidate/census/{index}.json')['reduced']
            row.update(record='adopted #255 candidate',classification=state['classification'],resolved_trials=state['resolved'],
                       final_success=state['parent_admitted'],failed_trial_optimizers=state['failed_optimizers'],
                       missing_trials=9-state['trials'],trial_unresolved=state['unresolved_trials'],
                       source_path=f'adoption-297/candidate/census/{index}.json',engine_wheel_sha256=SHA,
                       parameter_sha256=sha(RECORDS['candidate']),evidence_class='fresh numerical verification')
        else:
            row.update(engine_wheel_sha256='0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804',
                       parameter_sha256='efb2a9abe3787410734394f5ee32e6eade42d7cb6f5ad23445a357423690b2f3',
                       evidence_class='historical comparison; not rerun')
        rows.append(row)
    e.table(OUT/'paper-evidence/phase-family.csv',rows)
    restricted = r.read(r.CHAIN/'restricted-2/attempt-3/spec.json')['information_coordinates']
    values = r.s.parameter_values(r.s.parameter_mapping(RECORDS['candidate']))
    departures = [dict(identity=q['identity'],value=values[q['identity']],restricted_bounds=q['bounds'])
                  for q in restricted if q['identity'] in values and not q['bounds'][0]<=values[q['identity']]<=q['bounds'][1]]
    write('restricted-bound-departures.json',departures)


def evidence():
    import candidate_evidence_255 as e
    import shutil
    verify()
    original_copy = e.copy_of
    def copy_of(name, source, subs, truncate=None):
        path = original_copy(name, source, subs, truncate)
        text = path.read_text().replace('os.cpu_count()', "int(os.environ['AGENT_HEAVY_CORES'])")
        if "SPEC = json.loads((BASE/'spec.json').read_text())" in text:
            engine = dict(wheel_path=str(WHEEL.relative_to(r.ROOT)), wheel_sha256=SHA,
                          packages={k: importlib.metadata.version(k) for k in ('epcsaft','numpy','scipy')})
            text = text.replace("SPEC = json.loads((BASE/'spec.json').read_text())",
                                "SPEC = json.loads((BASE/'spec.json').read_text())\nSPEC['engine'] = " + repr(engine))
        path.write_text(text)
        return path
    e.copy_of = copy_of
    e.EV = OUT / 'producers'
    e.RECORDS = {'candidate': RECORDS['candidate']}
    e.assessment('candidate')
    # Reuse the existing point-data producer with this qualification's fixed replay.
    saved = r.OUT
    r.OUT = OUT
    r.write('wide/replay.json', r.read(OUT / 'candidate/replay.json')['rows'])
    e.point_data('candidate', 'wide')
    r.OUT = saved
    curves = e.curves('candidate')
    if not (e.EV / 'candidate/model-curves/summary.json').exists():
        e.run('candidate', curves, [])
    e.kim('candidate', curves)
    e.density('candidate')
    e.heat_capacity('candidate')
    package = OUT / 'paper-evidence'
    shutil.copytree(e.EV / 'candidate', package, dirs_exist_ok=True)
    shutil.copyfile(RECORDS['candidate'], package / 'reported-parameters.json')


def inventory():
    """Refresh hashes; current outputs require an explicit #297 producer and a change from BASE."""
    bundle = str(r.B.relative_to(r.ROOT))
    owners = {}
    for stem in ('heat-capacity', 'heat-of-absorption', 'loaded-density-errors', 'matin-pool', 'pressure',
                 'pressure-parity', 'pressure-residuals', 'speciation', 'species-parity', 'species-residuals'):
        for suffix in ('pdf', 'png', 'svg'):
            owners[f'{bundle}/figures/a7_regression_overview/output/{stem}.{suffix}'] = 'render_regression_overview.py'
    for name in ('density-statistics.csv', 'pressure.csv', 'speciation.csv', 'statistics.csv', 'provenance.json'):
        owners[f'{bundle}/figures/a7_regression_overview/output/{name}'] = 'render_regression_overview.py'
    owners[f'{bundle}/figures/a7_regression_overview/output/parameter-table-inputs.json'] = 'render_parameter_tables.py'
    for directory, names in [('figures/speciation/output', ('speciation-model.csv', 'speciation-observations.csv',
                              'speciation-model-grid.csv', 'speciation-display-observations.csv')),
                             ('figures/pressure/output', ('pressure-model.csv', 'pressure-observations.csv')),
                             ('results', ('figure-calculation-failures.csv', 'current-best-fit-residuals.csv',
                                          'current-best-fit-statistics.csv', 'figure-calculation-record.json'))]:
        owners.update({f'{bundle}/{directory}/{name}': 'generate_figure_data.py' for name in names})
    owners.update({f'analyses/solvent_specification_mea/results/{name}': 'analyses/solvent_specification_mea/run.py'
                   for name in ('continuation.json', 'endpoint-checks.json', 'predictions.json', 'runtime.json')})
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', BASE, '--'], cwd=r.ROOT, text=True).splitlines())
    untracked = set(subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=r.ROOT, text=True).splitlines())
    excluded = {'inventory.json', 'changed-files.json'}
    entries = {}
    for entry in r.read(OUT/'inventory.json'):
        path = r.ROOT/entry['path']
        if not path.is_file() or path.name in excluded:
            continue
        if entry['evidence_class'] == 'current adopted record output':
            if entry['path'] not in changed or entry['path'] not in owners:
                continue
            entry.update(producer_command=owners[entry['path']], changed_from_base=BASE)
        entries[entry['path']] = entry
    for name in changed | untracked:
        path = r.ROOT/name
        if path.is_file() and path.is_relative_to(OUT) and path.name not in excluded and name not in entries:
            entries[name] = dict(path=name, evidence_class='adoption evidence or declaration', wheel_sha256=None,
                                 parameter_sha256=None)
    for name, entry in entries.items():
        entry['sha256'] = sha(r.ROOT/name)
    (OUT/'inventory.json').write_text(json.dumps(sorted(entries.values(), key=lambda x:x['path']), indent=1)+'\n')
    previous = {x['path']:x for x in r.read(OUT/'changed-files.json')}
    final = []
    for name in sorted(changed | untracked):
        path = r.ROOT/name
        if path.is_file() and name != str((OUT/'changed-files.json').relative_to(r.ROOT)):
            entry = previous.get(name, dict(path=name, category='retained adoption evidence' if path.is_relative_to(OUT)
                                             else 'executable consumer or notebook'))
            entry['sha256'] = sha(path)
            final.append(entry)
    (OUT/'changed-files.json').write_text(json.dumps(final, indent=1)+'\n')
    print('inventory entries', len(entries), 'current adopted record outputs',
          sum(x['evidence_class']=='current adopted record output' for x in entries.values()), flush=True)


def adopt():
    """Replace the selected document and its solvent declaration in the adoption commit."""
    import shutil
    import tomllib
    assert all(x['passed'] for x in r.read(OUT/'f1.json').values())
    assert r.read(OUT/'f2.json')['passed']
    mapping = r.s.parameter_mapping(RECORDS['candidate'])
    spec = r.bind(mapping)
    an = r.ROOT/'analyses/solvent_specification_mea'
    declaration = an/'declarations.toml'
    text = declaration.read_text()
    chemistry = tomllib.loads(text)['chemistry']
    laws = {x['name']: x['correlation'] for x in spec.spec['chemistry']['reactions']['aqueous']}
    for group in chemistry['reactions'].values():
        for reaction in group:
            if reaction['name'] in ('R2', 'R5'):
                for key in ('a', 'b', 'c', 'd', 'e', 'f', 'reference_temperature'):
                    reaction['correlation'][key] = laws[reaction['name']][key]
    def toml(value):
        if isinstance(value, dict):
            return '{' + ', '.join(json.dumps(k)+' = '+toml(v) for k, v in value.items()) + '}'
        if isinstance(value, list):
            return '[' + ', '.join(map(toml, value)) + ']'
        return json.dumps(value)
    lines = text.splitlines()
    lines = ['chemistry = '+toml(chemistry) if line.startswith('chemistry = ') else line for line in lines]
    declaration.write_text('\n'.join(lines)+'\n')
    for destination in (r.B/'results/selected-current-best-parameters.json', an/'inputs/endpoint.json'):
        shutil.copyfile(RECORDS['candidate'], destination)
    config = an/'MEA.toml'
    text = config.read_text()
    old = tomllib.loads(text)
    text = text.replace(old['declarations']['sha256'], sha(declaration))
    text = text.replace(old['endpoint']['sha256'], sha(RECORDS['candidate']))
    config.write_text(text)
    replay = r.read(OUT/'candidate/replay.json')
    reference = [dict(target=x['identity'], predicted=x['value'], residual=x['residual'],
                      weighted_residual=x['weighted_residual'], cost=x['cost']) for x in replay['rows']]
    r.s.write_json(an/'inputs/reference.json', reference)
    inherited = r.read(r.ROOT/CONFIG['inherited_values'])[CONFIG['inherited_record']]
    inherited.update(parameter_sha256=sha(RECORDS['candidate']), wheel_sha256=SHA,
        owner_decision=CONFIG['owner_decision'],
        part_ii_rule="Each Part II amine ion's Born diameter is tied to its segment diameter; water–bicarbonate follows the adopted MEA record.")
    write('part-ii-shared-values.json', inherited)
    write('shared-hashes.json', {'part-ii-shared-values.json': sha(OUT/'part-ii-shared-values.json'),
                               'parameter_document': sha(RECORDS['candidate']), 'engine_wheel': SHA})


def default_check():
    subprocess.run([sys.executable, str(r.ROOT/'analyses/solvent_specification_mea/run.py')], check=True)
    an = r.ROOT/'analyses/solvent_specification_mea'
    values = r.read(an/'results/predictions.json')
    reference = r.read(OUT/'candidate/replay.json')['rows']
    differences = [relative(x['value'], y['value']) for x, y in zip(values, reference, strict=True)]
    assert [x['identity'] for x in values] == [x['identity'] for x in reference]
    assert len(values) == 307 and max(differences) <= 1e-10
    write('default-path.json', dict(rows=len(values), maximum_relative_prediction_difference=max(differences),
        parameter_sha256=sha(an/'inputs/endpoint.json'), declarations_sha256=sha(an/'declarations.toml'),
        cost=math.fsum(x['cost'] for x in values), passed=True))


CONFIG = {}
if __name__ == '__main__':
    if len(sys.argv) > 2:
        CONFIG = r.read(sys.argv[2])
        OUT = r.ROOT / CONFIG['output']
        BASE = CONFIG['base']
        RECORDS = {k: r.ROOT / v for k, v in CONFIG['records'].items()}
    {'adopt': adopt, 'default': default_check, 'f1': f1, 'f2': f2, 'f3': f3, 'evidence': evidence, 'uncertainty': uncertainty, 'shared': shared_values, 'extras': extras, 'f5': f5, 'phase-export': phase_export, 'inventory': inventory}[sys.argv[1]]()
