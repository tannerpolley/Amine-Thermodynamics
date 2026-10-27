"""Retained inputs and numerical reconciliation for the manuscript displays (#211): Engine 3e83e19c evidence of #213, #214 and #215."""
import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
E = BUNDLE / 'results/engine-3e83e19c-paper-evidence'  # #215 one-wheel package
D = BUNDLE / 'results/engine-3e83e19c-density-free'  # #213 density-free fit and limits
P = BUNDLE / 'results/engine-3e83e19c-phase-search/run-2'  # #214 162-state search
CHAIN = BUNDLE / 'results/engine-3e83e19c-refit-chain'  # #212
SELECTED = BUNDLE / 'results/selected-current-best-parameters.json'
# #212's density rule (association_volume_refit_chain.py:126): misses beyond 2s may only be these rows.
PERMITTED_MISSES = {'Amundsen2009_state_081', 'Hartono2014_density_80C_alpha0.29', 'Hartono2014_density_80C_alpha0.39'}
# #215's inventory binds this generator's literature and nomenclature strings at its merge commit; #211 edits the rest.
TABLE_GENERATOR, INVENTORY_COMMIT = 'docs/scientific/latex/scripts/final_rerun_tables.py', '771410a94f7729915bfe6457bfe7a5a0746f1611'
# Inputs outside #215's inventory: the display code itself and the Wagner Table 4 loading transcription (no Engine value).
UNINVENTORIED = {'analyses/mea_parameter_bundle/scripts/a7_presentation.py', 'analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py',
                 'analyses/mea_parameter_bundle/scripts/manuscript_style.py', 'docs/scientific/latex/supplement.tex'}
# Source-only data read by the figures but absent from #215's inventory: pinned here by SHA-256.
PINNED = {'analyses/mea_parameter_bundle/results/temperature-reanchor-140/never-accessed-vle-admission.csv':
          'ceee9107ca784936126b9f32e08af8cb1e9a7088a87b4667796d9abac94f5bcc'}
INPUTS = {}


def bind(path):
    path, key = Path(path), str(Path(path).relative_to(ROOT))
    INPUTS[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert PINNED.get(key, INPUTS[key]) == INPUTS[key], key  # pinned source data fails before use
    return path


def load(path):
    return json.loads(bind(path).read_text())


def rows(path):
    with bind(path).open(newline='') as stream:
        return list(csv.DictReader(stream))


def close(a, b):
    a, b = float(a), float(b)
    assert abs(a-b)/max(abs(a), abs(b), 1e-300) <= 1e-10, (a, b)


def coefficients(node):
    if isinstance(node, dict):
        if 'identity' in node and isinstance(node.get('value'), dict):
            yield node['identity'], node
        for value in node.values():
            yield from coefficients(value)
    elif isinstance(node, list):
        for value in node:
            yield from coefficients(value)


def stats(part, observed='observed', predicted='predicted'):
    errors = [float(r[predicted]) - float(r[observed]) for r in part]
    return dict(n=len(part), RMSE=math.sqrt(math.fsum(x*x for x in errors)/len(part)),
                bias=math.fsum(errors)/len(part),
                AARD_percent=100*math.fsum(abs(x/float(r[observed])) for x, r in zip(errors, part))/len(part))


def record_identity(parameter_sha256, engine):
    return dict(parameter_sha256=parameter_sha256, engine=dict(engine,
                commit=Path(engine['wheel_path']).parts[-2].removeprefix('main-')))


def checked():
    bind(Path(__file__))
    for path, digest in load(E / 'input-hashes.json').items():
        if path != TABLE_GENERATOR:  # checked against its inventoried commit in inventoried()
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    fit, summary = load(E / 'fit-summary.json'), load(E / 'summary.json')
    document = load(SELECTED)
    assert INPUTS[str(SELECTED.relative_to(ROOT))] == fit['record_sha256']
    assert bind(E / 'reported-parameters.json').read_bytes() == SELECTED.read_bytes()
    fitted = rows(E / 'fitted-rows.csv')
    assert len(fitted) == len({r['id'] for r in fitted}) == 307
    retained = {r['target']: r for r in load(E / 'full-replay.json')}
    assert set(retained) == {r['id'] for r in fitted}
    for row in fitted:
        original = retained[row['id']]
        for field in ('observed','predicted','scale','weight','residual','weighted_residual','cost'):
            assert float(row[field]) == original[field], (row['id'], field)
        assert row['form'] == original['form']
    for name in ('summary.json','state-summary.json','state-targets.csv','density.csv','cp.csv','carbonate-share.csv'):
        assert bind(E / 'selected-assessment' / name).read_bytes() == bind(E / name).read_bytes()
    for group, expected in fit['groups'].items():
        if group.startswith('common149 '):
            quantity = dict(pressure='PartialPressure', species='PhaseMoleFraction', heat='AdditionEnthalpy')[group.split()[1]]
            part = [r for r in fitted if r['group'] == 'common149' and r['quantity'] == quantity]
        else:
            part = [r for r in fitted if r['group'] == group]
        assert len(part) == expected['n'], group
        close(math.fsum(float(r['cost']) for r in part), expected['cost'])
        close(stats(part)['AARD_percent'], expected['AARD_percent'])
    close(math.fsum(float(r['cost']) for r in fitted), fit['cost'])
    score = load(E / 'reported-score.json')
    assert score['parameter_sha256'] == fit['record_sha256']
    close(fit['cost'], score['cost'])
    close(fit['groups']['common149']['cost'], score['C149'])
    for r in fitted:
        close(r['cost'], .5*float(r['weight'])*float(r['residual'])**2)
        close(r['weighted_residual'], math.sqrt(float(r['weight']))*float(r['residual']))
    spec = load(CHAIN / 'restricted-2/attempt-3/spec.json')
    density, heat, phase = (rows(E / name) for name in ('density.csv', 'heat.csv', 'phase-family.csv'))
    assert len(density) == len({r['id'] for r in density}) == 210
    loaded = [r for r in density if r['id'] in spec['loaded_density_ids']]
    assert len(loaded) == len(spec['loaded_density_ids']) == 47
    misses = {r['id'] for r in loaded if abs(float(r['error_over_s'])) > 2}
    assert misses <= PERMITTED_MISSES and len(loaded) - len(misses) == score['loaded_within_2s'], misses
    assert max(map(abs, score['co2_free_errors'].values())) <= 1
    assert len(heat) == len({r['id'] for r in heat}) == 22
    for source, n in [('Vinjarapu2024', 8), ('Arcis2011', 14)]:
        part = [r for r in heat if r['source'] == source]
        assert len(part) == n
        reduction = stats(part, 'observed_kJ_mol', 'predicted_kJ_mol')
        for key in ('RMSE', 'bias', 'AARD_percent'):
            close(reduction[key], summary['heat'][source][key])
    state = rows(E / 'state-targets.csv')
    assert len(state) == len({(r['kind'], r['identity'], r['target']) for r in state}) == 462
    for name, expected in load(E / 'state-summary.json')['scores'].items():
        part = [r for r in state if r['identity'] in expected['state_ids'] and r['target'] in expected['row_ids']]
        assert len(part) == expected['n_available'], name
        calculated = stats(part)
        for key in ('RMSE', 'bias', 'AARD_percent'):
            close(calculated[key], expected[key])
    coordinates = rows(E / 'conditional-standard-errors.csv')
    assert len(coordinates) == len(fit['coordinates']) == 16
    for c, retained in zip(coordinates, fit['coordinates'], strict=True):
        assert c['identity'] == retained['identity'] and c['unit'] == retained['unit']
        close(c['value'], retained['value'])
    assert [int(c['optimizer_column']) for c in coordinates if c['bound_active']=='True'] == fit['active_bounds']
    assert len(fit['active_bounds']) == 6
    # One 162-state grid; both fits share its states, whose reference pressures are the reported fit's bubble pressures.
    assert bind(P / 'phase-family.csv').read_bytes() == (E / 'phase-family.csv').read_bytes()
    assert load(P / 'provenance.json')['parameters']['reported']['parameter_bytes_sha256'] == fit['record_sha256']
    reference = {(r['temperature_K'], r['loading']): float(r['reference_pressure_Pa']) for r in rows(P / 'reference-pressures.csv')}
    assert len(reference) == 54
    paired = {name: {int(r['index']): r for r in phase if r['record'] == name} for name in ('comparison', 'reported')}
    assert len(phase) == 324 and set(paired['comparison']) == set(paired['reported']) == set(range(162))
    for index, a in paired['reported'].items():
        for field in ('temperature_K', 'loading', 'fraction', 'pressure_Pa', 'reference_pressure_Pa'):
            assert a[field] == paired['comparison'][index][field]
        assert float(a['reference_pressure_Pa']) == reference[a['temperature_K'], a['loading']]
        close(a['pressure_Pa'], float(a['fraction'])*float(a['reference_pressure_Pa']))
    for r in phase:
        assert r['admitted'] == r['final_success'] == 'True' and int(r['failed_trial_optimizers']) == int(r['missing_trials']) == int(r['trial_unresolved']) == 0
    counts = rows(P / 'counts-by-temperature.csv')
    for name, part in paired.items():
        assert sum(int(r['resolved_trials']) > 0 for r in part.values()) == sum(int(c['descent_states']) for c in counts if c['record'] == name)
    assert sum(int(r['resolved_trials']) > 0 for r in paired['reported'].values()) == 0
    return fit, summary, document, fitted, spec, density, heat, coordinates, paired


def inventoried():
    """Every bound input matches #215's inventory or its hashed producer inputs; the table generator keeps its inventoried source strings."""
    inventory = {e['path']: e['sha256'] for e in load(E / 'inventory.json')['entries']}
    hashed = load(E / 'input-hashes.json')
    adoption = load(E / 'adoption.json')  # anchors the inventory and the adopted selected bytes
    relative = lambda path: str(path.relative_to(ROOT))
    assert adoption['gates']['inventory.json'] == INPUTS[relative(E / 'inventory.json')]
    assert adoption['new_parameter_sha256'] == inventory[relative(E / 'reported-parameters.json')] == INPUTS[relative(SELECTED)]
    anchors = {relative(E / name) for name in ('inventory.json', 'input-hashes.json', 'adoption.json')} | {relative(SELECTED)}
    assert inventory[TABLE_GENERATOR] == hashed[TABLE_GENERATOR]
    old = subprocess.run(['git', '-C', str(ROOT), 'show', f'{INVENTORY_COMMIT}:{TABLE_GENERATOR}'], capture_output=True, check=True).stdout
    assert hashlib.sha256(old).hexdigest() == inventory[TABLE_GENERATOR]
    old, new = old.decode(), (ROOT / TABLE_GENERATOR).read_text()
    for marker in ('literature=[', 'symbols=['):
        start = old.index(marker)
        assert all(line in new for line in old[start:old.index(']]', start)+2].splitlines() if 'This work' not in line), marker
    # #211 Part 2 permits only the approved present-work row and parameter-count caption.
    for marker, digest in {
        "['This work'": '4e353b4fc3fd38196e1982b0248d2e242f3f2d183903a2d58d6a9ad942f282b5',
        "table('literature_model_comparison.tex'": 'ac15b51184425c0833be514310ed22ce356d10ea23eeada8594fabb30b412772',
    }.items():
        line, = (line for line in new.splitlines() if marker in line)
        assert hashlib.sha256(line.encode()).hexdigest() == digest, marker
    for path, digest in INPUTS.items():
        if path in UNINVENTORIED or path in anchors or path == TABLE_GENERATOR:
            continue
        assert PINNED.get(path) or inventory.get(path, hashed.get(path)) == digest, path
