"""Fixed 2026 record through Part I's retained assessment producer."""
import sys
import subprocess
from functools import partial
import adoption_297 as a
import candidate_evidence_255 as e
OUT = e.B / 'results/same-data-comparison'
e.EV = OUT / 'part1'
e.RECORDS = {'published': OUT / 'polley-2026-explicit-defaults.json'}
original_copy = e.copy_of

def copy_of(name, source, subs, truncate=None):
    path = original_copy(name, source, subs, truncate)
    text = path.read_text().replace('os.cpu_count()', "int(os.environ['AGENT_HEAVY_CORES'])")
    text = text.replace("SPEC = json.loads((BASE/'spec.json').read_text())", "SPEC = json.loads((BASE/'spec.json').read_text())\nSPEC['engine'] = " + repr(dict(wheel_path=str(a.WHEEL), wheel_sha256=a.SHA, commit=a.COMMIT)))
    text = text.replace("FIT/'run/fit/usable-budget-endpoint.json'", f"Path({str(e.RECORDS[name])!r})")
    path.write_text(text)
    return path

e.copy_of = copy_of

def kim():
    assessed = e.EV / 'published/selected-assessment'
    for filename in ('heats.csv', 'state-targets.csv'):
        rows = e.rows(assessed / filename)
        if filename == 'state-targets.csv':
            rows = [r for r in rows if r['quantity'] == 'species' and r['kind'] == 'packet']
        e.table(e.EV / 'published' / ('heat.csv' if filename == 'heats.csv' else 'species-figure-data.csv'), rows)
    e.kim('published', e.curves('published'))


CENSUS = e.r._census

def supplied_census(task):
    import phase_diagnosis_255 as p
    mapping, state, path = task
    native = p.f.stability
    phases = []
    sources = []
    for filename in sorted(p.OLD.glob('*/split-seeded-' + str(state['index']) + '-trial-*.json')):
        split = e.r.read(filename)
        if split.get('confirmed'):
            sources.append(str(filename.relative_to(e.ROOT)))
            phases.extend(p.f.eq.Phase('earlier-' + str(len(phases) + i), kind='liquid',
                support=phase['support'], composition_guess=phase['mole_fractions'])
                for i, phase in enumerate(split['result']['phases']) if phase['role'] == 'liquid')
    def checked(model, problem, result):
        report = native(model, problem, result)
        report['supplied_sources'] = sources
        report['supplied'] = native(model, problem, result, supplied=phases) if phases else None
        return report
    p.f.stability = checked
    try:
        return CENSUS(task)
    finally:
        p.f.stability = native


def census():
    e.r._census = supplied_census
    e.r.OUT = e.EV
    for name, path in [('published', e.RECORDS['published']), ('current', a.RECORDS['candidate'])]:
        print(name, e.r.census(e.s.parameter_mapping(path), name), flush=True)


def historical_calorics():
    import evaluate_direct_absorption_heat as heat
    import verify_solution_heat_capacity as cp
    path = e.RECORDS['published']
    mapping = e.s.parameter_mapping(path)
    directory = e.EV / 'historical-calorics'
    directory.mkdir(exist_ok=True)
    for function in (e.s.parameter_mapping, e.s.load_parameters):
        function.__defaults__ = (path,)
    packet = e.s.load_state_packet(OUT / 'qualification-inputs.json.gz')
    e.s.load_state_packet = lambda: packet
    cp.OUTPUT = directory / 'cp'
    cp.main()
    observations = subprocess.check_output(['git', 'show', '799b201:analyses/mea_parameter_bundle/data/input/calorimetry-observation-partition.csv'])
    (directory / 'heat-inputs.csv').write_bytes(observations)
    heat.load_packet = lambda: packet
    heat.evaluate_state = partial(e.s.evaluate_state, mapping=mapping, parameter_path=path)
    e.s.RUNS = directory / 'cache'
    model = heat.epcsaft.Mixture(heat.epcsaft.Parameters.from_mapping(mapping), thermochemistry=heat.vrc.record())
    source = [r for r in heat.read_rows(directory / 'heat-inputs.csv') if r['regression_eligible'] == 'true']
    states, attempts, rows = heat.score(e.s.reaction_values(mapping), model, e.s.parameter_fingerprint(mapping), source, heat.EvaluationLimits())
    heat.write_rows(directory / 'heat.csv', rows)
    e.s.write_json(directory / 'heat-states.json', states)
    e.s.write_json(directory / 'provenance.json', dict(parameter_sha256=e.sha(path), wheel_sha256=a.SHA,
        engine_commit=a.COMMIT, packet_sha256=e.sha(OUT / 'qualification-inputs.json.gz'), heat_inputs_sha256=e.sha(directory / 'heat-inputs.csv')))


def ratios():
    values, ok, _ = e.r.replay(e.s.parameter_mapping(e.RECORDS['published']),
        rows=lambda spec: [r for r in spec.inputs['observations']['fitted'] if r['group'] == 'Jakobsen'])
    assert ok and len(values) == 6
    e.s.write_json(e.EV / 'published/ratios.json', values)


def scores():
    import kim2007_heat_pathways as k
    directories = [e.EV / 'published/selected-assessment', e.B / 'results/adoption-297/paper-evidence']
    records = [e.rows(d / 'state-targets.csv') for d in directories]
    fitted = {r['id'] for r in e.rows(directories[1] / 'fitted-rows.csv')}
    result = []
    def add(group, pairs, predicted, observed, metric, roles):
        values = [k.metrics([dict(record_id=r.get('target') or r.get('identity') or r.get('id') or r.get('T_K'), predicted=float(r[predicted]), observed=float(r[observed])) for r in rr if r[predicted] not in (None, '', 'None')]) for rr in pairs]
        result.append(dict(group=group, n=[v['n'] for v in values], roles=roles, metric=metric,
                           deviations=[v['aard_percent' if metric == 'AARD (%)' else 'rmse'] for v in values]))
    for label, selected in [('Six-source pressures', lambda r: r['kind']=='canonical'),
            ('47 current-fitted pressures', lambda r: r['kind']=='canonical' and r['target'] in fitted),
            ('112 current-not-fitted pressures', lambda r: r['kind']=='canonical' and r['target'] not in fitted),
            ('Species fractions', lambda r: r['quantity']=='species')]:
        add(label, [[r for r in rr if selected(r)] for rr in records], 'predicted', 'observed',
            'AARD (%)' if 'pressure' in label else 'RMSE (mole fraction)', ['fitted / not fitted; see role note', 'fitted' if label.startswith('47') else 'not fitted' if label.startswith('112') else '101 fitted / 30 not fitted' if label=='Species fractions' else '47 fitted / 112 not fitted'])
    add('Species ratios', [e.r.read(e.EV/'published/ratios.json'), [r for r in e.r.read(a.OUT/'candidate/replay.json')['rows'] if r['group']=='Jakobsen']],
        'value', 'observed', 'AARD (%)', ['formulation not fitted; measurements used in earlier ion fit', 'fitted'])
    add('Jakobsen carbonate share', [e.rows(d/'carbonate-share.csv') for d in directories],
        'predicted_share', 'observed_share', 'AARD (%)', ['formulation not fitted; measurements used in earlier ion fit', 'not fitted; previously assessed'])
    for source in ('Vinjarapu2024','Arcis2011'):
        add(source+' heats', [[r for r in e.rows(d/'heats.csv' if i==0 else d/'heat.csv') if r['source']==source] for i,d in enumerate(directories)],
            'predicted_kJ_mol', 'observed_kJ_mol', 'RMSE (kJ/mol CO2)', ['not fitted', 'fitted' if source=='Vinjarapu2024' else 'not fitted'])
    for source, loaded in [('Amundsen2009',True),('Amundsen2009',False),('Hartono2014',True),('Han2012',True)]:
        add(source+(' all' if source=='Han2012' else ' loaded' if loaded else ' CO2-free'), [[r for r in e.rows(d/'density.csv') if r['source']==source and (source=='Han2012' or (float(r['loading'])>0)==loaded)] for d in directories],
            'predicted_kg_m3', 'observed_kg_m3', 'RMSE (kg/m3)', ['not fitted', 'fitted / not fitted' if source!='Han2012' else 'not fitted'])
    add('Four Hilliard heat capacities', [e.rows(d/'cp.csv') for d in directories], 'equilibrium_cp_kJ_kg_K', 'observed_kJ_kg_K', 'AARD (%)', ['not fitted','fitted'])
    for group in ('broad Cp','Weiland1997 comparison','Concepcion2023 comparison'):
        add(group, [[r for r in e.r.read(d/'heat-capacity-264.json')['rows'] if r['group']==group] for d in [e.EV/'published',directories[1]]],
            'predicted_kJ_kg_K','observed_kJ_kg_K','AARD (%)',['not fitted','2 fitted / 49 not fitted' if group=='broad Cp' else 'not fitted'])
    add('Wagner pressures', [[r for r in rr if r['kind']=='wagner'] for rr in records],
        'predicted','observed','AARD (%)',['not fitted','not fitted'])
    for w in (15,45):
        summaries = [e.r.read(d/'state-summary.json')['scores'][f'transfer {w} wt%'] for d in directories]
        result.append(dict(group=f'Aronu {w} wt% pressures', n=[r['n_total'] for r in summaries], roles=['comparison only','not fitted'],metric='AARD (%)',deviations=[r['AARD_percent'] for r in summaries]))
    for temperature in (313.15,353.15,393.15):
        add(f'Kim heat {temperature:g} K', [[r for r in e.rows(d/'kim2007-heat-pathways/kim-heat.csv') if float(r['T_K'])==temperature] for d in [e.EV/'published',directories[1]]],
            'predicted','observed','RMSE (kJ/mol CO2)',['fitted / not fitted' if temperature<393 else 'not fitted','not fitted'])
    e.s.write_json(OUT/'part1-scores.json', result)
    lines = ['| Observation group | n (2026/current) | 2026 role | Current role | Metric | 2026 | Current |', '|---|---:|---|---|---|---:|---:|']
    lines += ['| '+ ' | '.join([r['group'], '/'.join(map(str,r['n'])), *r['roles'], r['metric'], *(f'{v:.8g}' for v in r['deviations'])])+' |' for r in result]
    (OUT/'part1-table.md').write_text('\n'.join(lines)+'\n')


def caloric_differences():
    differences = []
    for kind, key, old_q, new_q, unit, new_file in [
            ('heat','record_id','predicted_heat_release_kj_per_mol_CO2','predicted_heat_release_kj_per_mol_CO2','kJ/mol CO2','heat.csv'),
            ('cp','T_K','equilibrium_cp_kJ_per_kg_K','equilibrium_cp_kJ_per_kg_K','kJ/(kg K)','cp/heat_capacity.csv')]:
        current = {r[key]: r for r in e.rows(e.EV/'historical-calorics'/new_file)}
        for reference in e.rows(OUT/('historical-'+kind+'.csv')):
            row = current[reference[key]]
            if reference[old_q] and row[new_q]:
                old, new = float(reference[old_q]), float(row[new_q])
                differences.append(dict(quantity=kind,identity=reference[key],reference=old,value=new,
                    difference=new-old,relative_difference=new/old-1,unit=unit))
    e.table(OUT/'caloric-reference-differences.csv',differences)


if __name__ == '__main__':
    e.s.verify_wheel()
    assert e.sha(e.RECORDS['published']) == 'be66f6cf9df77201a632d73a3c3e341f66ce7fc77b69c3d657288f4c1899a76b' and e.sha(a.RECORDS['candidate']) == 'f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97'
    {'assessment': lambda: e.assessment('published'), 'kim': kim, 'census': census,
     'cp': lambda: e.heat_capacity('published'), 'historical-calorics': historical_calorics, 'ratios': ratios, 'scores': scores, 'caloric-differences': caloric_differences}[sys.argv[1]]()
