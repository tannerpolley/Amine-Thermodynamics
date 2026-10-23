"""Re-run every parameter fit behind the manuscript on the pinned Engine 3e83e19c wheel (#207). Each retained declaration is
copied with only its Engine fields changed, the retained producer runs unchanged, and every endpoint coefficient is compared
with the retained endpoint. Writes results/engine-3e83e19c-refits/<mode>/. Run from the checkout root, one mode per process:
    nice -n 10 .venv/bin/python analyses/mea_parameter_bundle/scripts/engine_3e83e19c_refits.py MODE
Modes: water | stage2 | co2-slope | stage5 | a6 | restricted | restricted-2 | displays | compare."""
import hashlib, importlib.metadata, json, math, sys
from pathlib import Path
ROOT = Path.cwd()
B = ROOT / 'analyses/mea_parameter_bundle'
sys.path[:0] = [str(B / 'scripts'), str(B / 'calibration-misfit'), str(ROOT / 'src')]
import a7_presentation as a, fit_campaign as c

R, J = B / 'results', B / 'results/joint-recalibration-170'
OUT = R / 'engine-3e83e19c-refits'
WHEEL = next((ROOT / 'build/engine-wheels/main-3e83e19ccc771b51d8ebc038931ab25192f4c5b5').glob('*.whl')).relative_to(ROOT)
ENGINE = dict(wheel_path=str(WHEEL), wheel_sha256=hashlib.sha256((ROOT / WHEEL).read_bytes()).hexdigest(),
              packages={p: importlib.metadata.version(p) for p in ('epcsaft', 'numpy', 'scipy')})
# mode: (retained declaration, case ids, retained endpoint records to compare: new path relative to the run -> retained path)
FITS = {
    'water': (R / 'water-124/spec.json', ['water-124'], {'lambda-0.1-A/parameters.json': R / 'water-124/lambda-0.1-A/parameters.json'}),
    'stage2': (J / 'stage2/spec.json', ['stage2'], {'neutral-mea-water/A/parameters.json': J / 'stage2/neutral-mea-water/A/parameters.json'}),
    'co2-slope': (J / 'stage2/co2-water/slope/spec.json', ['stage2'], {'co2-water/B/parameters.json': J / 'stage2/co2-water/slope/co2-water/B/parameters.json'}),
    'stage5': (J / 'amendment-2/stage5-smaller-dV/stage5-spec.json', ['stage5'], {'larger-dV-parameters.json': J / 'amendment-2/stage5-smaller-dV/larger-dV-parameters.json'}),
}
# Joint fits: the declared information step writes release tests on this wheel, then the declared fit runs against them.
JOINT = {'a6': J / 'amendment-6/joint-mea-water/held/fit-spec.json', 'restricted': J / 'amendment-7/inputs/restricted-fit.json',
         'restricted-2': J / 'amendment-7/inputs/restricted-2-fit.json'}
for name, retained in [('a6', J / 'amendment-6/joint-mea-water/held'), ('restricted', J / 'amendment-7/restricted'), ('restricted-2', J / 'amendment-7/restricted-2')]:
    FITS[name] = (JOINT[name], ['stage6'], {'fit/usable-budget-endpoint.json': retained / 'fit/usable-budget-endpoint.json'})


# Engine 3e83e19c requires every absent association pair to be declared. Records written before #191 leave the CO2/MEA pair
# implicit; a translated copy states it exactly as the reported record does, which keeps the model unchanged.
NO_CROSS = dict(component_id_a='carbon-dioxide', component_id_b='monoethanolamine', provenance=dict(source_id='engine-3e83e19c-refits',
                locator='explicit form of the absent CO2/MEA association edge, as in the reported record (#191); added for Engine 3e83e19c (#207)'))


def translated(path, directory):
    try:
        record = json.loads((ROOT / path).read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict) or 'topology' not in record or any(
            {e['component_id_a'], e['component_id_b']} == {'carbon-dioxide', 'monoethanolamine'} for e in record['topology'].get('no_cross_association', [])):
        return None
    record['topology'].setdefault('no_cross_association', []).append(NO_CROSS)
    target = directory / Path(path).name.replace('.json', f'-{hashlib.sha256(str(path).encode()).hexdigest()[:8]}.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=2) + '\n')
    return str(target.relative_to(ROOT))


def repoint(node, moved):
    if isinstance(node, list):
        return [repoint(x, moved) for x in node]
    if isinstance(node, dict):
        node = {k: repoint(v, moved) for k, v in node.items()}
        for key in ('path', 'parameters_path'):
            if node.get(key) in moved.values() and 'sha256' in node:
                node['sha256'] = hashlib.sha256((ROOT / node[key]).read_bytes()).hexdigest()
        return node
    return moved.get(node, node) if isinstance(node, str) else node


def respec(source, target, translate=False, **changes):
    spec = json.loads(source.read_text())
    if translate:
        strings = {x for x in json.dumps(spec).split('"') if x.endswith('.json')}
        moved = {p: new for p in strings if (new := translated(p, target.parent / 'inputs'))}
        spec = repoint(spec, moved)
    spec['engine'] = dict(spec['engine'], **ENGINE)
    spec['inputs'] = [r for r in spec.get('inputs', []) if not r['path'].endswith('.whl')]
    spec.update(changes)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(spec, indent=2) + '\n')
    return target


def coefficients(path):
    d = json.loads(Path(path).read_text())
    return {i: n['value']['magnitude'] for i, n in a.coefficients({k: d[k] for k in ('components', 'pairs', 'correlations', 'model_coefficients', 'reaction_correlations', 'topology') if k in d})}


def compare(new, old):
    n, o = coefficients(new), coefficients(old)
    assert n.keys() == o.keys(), sorted(n.keys() ^ o.keys())
    diff = {k: abs(n[k] - o[k]) / max(abs(o[k]), 1e-300) for k in o if n[k] != o[k]}
    return dict(new=str(Path(new).relative_to(ROOT)), retained=str(Path(old).relative_to(ROOT)), coefficients=len(o),
                bitwise_equal=not diff, max_relative_difference=max(diff.values(), default=0.), differing=diff)


def displays():
    """Displayed values that the joint-fit replay does not cover, with the reported parameters (and the comparison fit) on this wheel."""
    import csv, shutil
    import fit_observations as o, heat_evidence_170 as he, reduce_a7_evidence as r, epcsaft
    out = OUT / 'displays'
    out.mkdir(parents=True, exist_ok=True)
    reported = o.s.parameter_mapping(a.SELECTED)
    # Water against IAPWS-95 at the 42 declared states (Fig. 1).
    water_spec = json.loads((R / 'water-124/spec.json').read_text())
    rows = o.water_assessment(water_spec, reported)['rows']
    assert len(rows) == 42 and all(x['evaluated'] for x in rows)
    with (R / 'water-124/lambda-0.1-A/water.csv').open() as f:
        fields = next(csv.reader(f))
    with (out / 'water.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    # Cai cost with the earlier constant MEA-water interaction and every other input reported (S10 limit base).
    spec = json.loads((OUT / 'restricted-2/spec.json').read_text())
    constant = o.s.with_parameter_values(reported, {'pair/monoethanolamine/water/k_ij': -0.0843938800264992, 'pair/monoethanolamine/water/k_ij/reciprocal_temperature_slope': 0.})
    _, declared = o.stage6_rows(spec, constant)
    weights = c.stage6_weights(spec, [x for x, _ in declared], 1.)
    cai = [(x['id'], item, wt) for (x, item), wt in zip(declared, weights, strict=True) if x['id'].startswith('cai1996')]
    cai_values = o.replay(constant, cai)
    assert len(cai_values) == 50 and all(v['status'] == 'Available' for v in cai_values)
    # Arcis heats for the reported and comparison fits (Table S23), through the assessment's heat call.
    heat_rows = [x for x in json.loads((ROOT / spec['heat_rows_path']).read_text()) if not x['record_id'].startswith('vinjarapu')]
    heats = {}
    for name, record in (('reported', a.SELECTED), ('comparison', J / 'amendment-6/joint-mea-water/held/fit/usable-budget-endpoint.json')):
        mapping = o.s.parameter_mapping(record)
        params = epcsaft.Parameters.from_mapping(mapping)
        errors = {}
        for x in heat_rows:
            v = o.predict(mapping, o.heat_items(mapping, params, [x], he.request(mapping, 313.15, .11)))[0]
            errors.setdefault(x['system_pressure_Pa'], []).append((v.value - x['observed_addition_enthalpy_J_per_mol_CO2']) / 1000)
        rmse = lambda e: math.sqrt(math.fsum(z * z for z in e) / len(e))
        heats[name] = dict(n=sum(map(len, errors.values())), RMSE_kJ_mol=rmse([z for e in errors.values() for z in e]),
                           by_pressure={str(p): dict(n=len(e), RMSE_kJ_mol=rmse(e), bias_kJ_mol=math.fsum(e) / len(e)) for p, e in errors.items()})
    # Conditional standard errors and correlations from the restricted-2 fit on this wheel.
    base = out / 'conditional-base'
    (base / 'restricted-2/fit').mkdir(parents=True, exist_ok=True)
    shutil.copy(OUT / 'restricted-2/run/fit/chemistry-coordinates.json', base / 'restricted-2/fit/chemistry-coordinates.json')
    r.BASE, r.OUT = base, out / 'conditional'
    r.OUT.mkdir(exist_ok=True)
    r.uncertainty(spec, json.loads((OUT / 'restricted-2/run/fit/native.json').read_text()), json.loads((OUT / 'restricted-2/run/fit/usable-budget-endpoint.json').read_text()))
    summary = dict(parameter_sha256=hashlib.sha256(a.SELECTED.read_bytes()).hexdigest(), engine=ENGINE,
                   cai_constant_interaction_cost=math.fsum(v['cost'] for v in cai_values), arcis=heats,
                   water_mean_absolute_relative_error={f'{g}/{q}': 100 * math.fsum(abs(float(x[q])) for x in rows if x['grid'] == g and q in x) / sum(x['grid'] == g and q in x for x in rows)
                                                       for g in ('primary', 'staggered', 'atmospheric-controls') for q in ('saturated_liquid_rho_error_relative', 'psat_error_relative', 'cp_error_relative')
                                                       if any(x['grid'] == g and q in x for x in rows)})
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


def main(mode):
    if mode == 'displays':
        return displays()
    if mode == 'compare':
        rows = {m: [compare(OUT / m / 'run' / new, old) for new, old in FITS[m][2].items()] for m in FITS if (OUT / m / 'run').exists()}
        (OUT / 'comparison.json').write_text(json.dumps(rows, indent=2) + '\n')
        print(json.dumps({m: [(r['new'], r['bitwise_equal'], r['max_relative_difference']) for r in v] for m, v in rows.items()}, indent=2))
        return
    source, cases, _ = FITS[mode]
    if mode in JOINT:
        declared = json.loads(source.read_text())
        start = declared['fit_case']['start']
        information = respec(source, OUT / mode / 'information-spec.json', information_starts=[x for x in declared['information_starts'] if x['id'] == start])
        trimmed = {k: v for k, v in json.loads(information.read_text()).items() if k not in ('fit_case', 'release_tests_path', 'release_tests_sha256')}
        information.write_text(json.dumps(trimmed, indent=2) + '\n')
        c.run(information, OUT / mode / 'release', case_ids=cases, operation='information')
        release = OUT / mode / 'release/release-tests.json'
        spec = respec(source, OUT / mode / 'spec.json', release_tests_path=str(release.relative_to(ROOT)), release_tests_sha256=hashlib.sha256(release.read_bytes()).hexdigest())
        c.run(spec, OUT / mode / 'run/fit', case_ids=cases, operation='fit')
        return
    spec = respec(source, OUT / mode / 'spec.json', translate=mode != 'water')
    c.run(spec, OUT / mode / 'run', case_ids=cases, operation='fit')


if __name__ == '__main__':
    main(sys.argv[1])
