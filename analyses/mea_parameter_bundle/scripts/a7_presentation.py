"""Retained inputs and numerical reconciliation for issue 197 presentation."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
E = BUNDLE / 'results/a7-paper-evidence'
J = BUNDLE / 'results/joint-recalibration-170'
F = BUNDLE / 'results/heat-final-170'
SELECTED = BUNDLE / 'results/selected-current-best-parameters.json'
INPUTS = {}


def bind(path):
    path = Path(path)
    INPUTS[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
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


def phase_identity(directory, engine):
    provenance = load(directory/'provenance.json')
    summary = load(directory/'summary.json')
    mapping = load(directory/'fixed-parameters.json')
    assert mapping == load(ROOT/provenance['source'])
    assert hashlib.sha256(json.dumps(mapping, sort_keys=True).encode()).hexdigest() == summary['parameter_sha256']
    identity = record_identity(provenance['source_sha256'], engine)
    assert identity['engine']['commit'] == provenance['engine_commit']
    assert engine['wheel_sha256'] == provenance['wheel_sha256']
    return dict(identity, fixed_parameter_sha256=INPUTS[str((directory/'fixed-parameters.json').relative_to(ROOT))],
                phase_mapping_sha256=summary['parameter_sha256'])


A6_ASSESSMENT_NOTE = "A6 density and Arcis assessment values retain parameter SHA-256 `ceefc95cd051fb291e0c08675c4cb6f159bf10dca0116ef1251ba78c243f79c7`, Engine commit `21e761c318c2ac5b555a245365c844d38a93e4cb`, and wheel SHA-256 `d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357`. The paired A6/A7 phase-family classifications were evaluated on Engine `8298c6029ebb8b467929badc4a223c580ec591ab`."


def checked():
    bind(Path(__file__))
    for path, digest in load(E / 'input-hashes.json').items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    fit, summary = load(E / 'fit-summary.json'), load(E / 'summary.json')
    document = load(SELECTED)
    assert INPUTS[str(SELECTED.relative_to(ROOT))] == fit['record_sha256']
    endpoint = J / 'amendment-7/restricted-2/fit/usable-budget-endpoint.json'
    assert bind(endpoint).read_bytes() == SELECTED.read_bytes()
    fitted = rows(E / 'fitted-rows.csv')
    assert len(fitted) == len({r['id'] for r in fitted}) == 307
    replay = load(J / 'amendment-7/restricted-2/replay/A7-restricted-2-full-replay.json')
    retained = {r['target']: r for r in replay}
    assert set(retained) == {r['id'] for r in fitted}
    for row in fitted:
        original = retained[row['id']]
        for field in ('observed','predicted','scale','weight','residual','weighted_residual','cost'):
            assert float(row[field]) == original[field], (row['id'], field)
        assert row['form'] == original['form']
    for name in ('summary.json','state-summary.json','state-targets.csv','density.csv','cp.csv','carbonate-share.csv'):
        assert bind(J / 'amendment-7/selected-assessment' / name).read_bytes() == (E / name).read_bytes()
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
    score = load(J / 'amendment-7/fixed-study/wheel-8298c602/restricted-2-endpoint/score.json')
    close(fit['cost'], score['cost'])
    close(fit['groups']['common149']['cost'], score['C149'])
    for r in fitted:
        close(r['cost'], .5*float(r['weight'])*float(r['residual'])**2)
        close(r['weighted_residual'], math.sqrt(float(r['weight']))*float(r['residual']))
    spec = load(J / 'amendment-7/restricted-2/fit-spec.json')
    density, heat, phase = (rows(E / name) for name in ('density.csv', 'heat.csv', 'phase-family.csv'))
    assert len(density) == len({r['id'] for r in density}) == 210
    loaded = [r for r in density if r['id'] in spec['loaded_density_ids']]
    assert len(loaded) == len(spec['loaded_density_ids']) == 47
    failures = [r for r in loaded if abs(float(r['error_over_s'])) > 2]
    assert {r['id'] for r in failures} == {'Amundsen2009_state_081', 'Hartono2014_density_80C_alpha0.29', 'Hartono2014_density_80C_alpha0.39'}
    assert all(float(r['T_K']) == 353.15 for r in failures)
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
    paired = {name: {int(r['index']): r for r in phase if r['record'] == name} for name in ('A6', 'A7')}
    assert len(phase) == 146 and set(paired['A6']) == set(paired['A7']) == set(range(73))
    for index, a in paired['A6'].items():
        for field in ('temperature_K', 'loading', 'pressure_Pa'):
            assert a[field] == paired['A7'][index][field]
    assert [sum(int(r['resolved_trials']) > 0 for r in paired[n].values()) for n in ('A6', 'A7')] == [12, 0]
    return fit, summary, document, fitted, spec, density, heat, coordinates, paired
