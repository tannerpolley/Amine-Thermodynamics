"""Render retained adopted MEA results (#297, Engine 391dfe5d) and explicitly historical comparisons; no Engine computation."""
import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
E = BUNDLE / 'results/adoption-297/paper-evidence'  # adopted MEA, Engine 391dfe5d
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
# #244 binds the retained MDEA parameter declarations used by the supplement.
PINNED.update({'analyses/mdea_mea_workflow/results/stage2-capped/A3/endpoint.json': '3e1a69baf8b20cfc2f7586c04aa9e2cf604e6ffda6a2bbbfcbe7d662e3dec0e8', 'analyses/mdea_mea_workflow/results/stage2-capped/A3/declaration.json': '86111af51bace3d696b9963cb84a4ac811cdb962f5d851b2c90237d72e7df53b', 'analyses/mdea_mea_workflow/results/stage2-capped/B1/endpoint.json': '1d0d80832f282cde85acab294501ca9ec8dbc34cddf8edf2eebf6e1e1d03949d', 'analyses/mdea_mea_workflow/results/stage2-capped/B1/declaration.json': 'b98bacbcbce32c8b508683d7ca53f66881039a1d509f393e5dd2fd2d6690b644'})
PINNED['analyses/mdea_mea_workflow/results/refit-298/B1-endpoint/endpoint.json'] = '2a5341be176829d087133a1467828f762a655f92a586eb1062a5719a58142d9d'
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


def reported_score():
    fit = load(E / 'fit-summary.json')
    m = load(E / 'reported-score.json')['metrics']['candidate']
    return dict(parameter_sha256=fit['record_sha256'], cost=fit['cost'],
                C149=fit['groups']['common149']['cost'],
                pressure_AARD_pct=m['fitted CO2 partial pressure']['aard_percent'],
                species_AARD_pct=m['fitted phase mole fraction']['aard_percent'],
                vinjarapu_rmse_kJ_mol=m['fitted heat of absorption']['rmse']/1000,
                loaded_within_2s=m['loaded density']['within_2s'], loaded_count=47,
                co2_free_errors={r['id']:float(r['error_kg_m3']) for r in rows(E/'density.csv')
                                 if r['id'] in {x['id'] for x in rows(E/'fitted-rows.csv') if x['group']=='CO2-free density'}})


def checked():
    bind(Path(__file__))
    fit, summary = load(E/'fit-summary.json'), load(E/'summary.json')
    document = load(SELECTED)
    assert INPUTS[str(SELECTED.relative_to(ROOT))] == fit['record_sha256'] == summary['parameter_sha256']
    assert bind(E/'reported-parameters.json').read_bytes() == SELECTED.read_bytes()
    assert fit['engine']['wheel_sha256'] == summary['engine_wheel_sha256']
    fitted = rows(E/'fitted-rows.csv')
    assert len(fitted) == len({r['id'] for r in fitted}) == 307
    replay = load(E/'full-replay.json')
    assert replay['parameter_sha256'] == fit['record_sha256']
    declarations = {r['identity']:r['row'] for r in replay['rows']}
    fitted = [dict(declarations[r['id']], **r, target=r['id'], declaration=str(declarations[r['id']])) for r in fitted]
    for r in fitted:
        r['form'] = {'log_ratio':'LogRatio', 'difference':'Difference'}.get(r['form'],r['form'])
        if 'scale' not in r:
            assert r['form']=='LogRatio'
            r['scale']=1.0  # unscaled logarithmic residual
    close(sum(float(r['cost']) for r in fitted), replay['cost'])
    for group, expected in fit['groups'].items():
        if group.startswith('common149 '):
            quantity = dict(pressure='PartialPressure', species='PhaseMoleFraction', heat='AdditionEnthalpy')[group.split()[1]]
            part = [r for r in fitted if r['group']=='common149' and r['quantity']==quantity]
        else:
            part = [r for r in fitted if r['group']==group]
        assert len(part)==expected['n'], group
        close(sum(float(r['cost']) for r in part), expected['cost'])
        close(stats(part)['AARD_percent'], expected['AARD_percent'])
    spec = load(CHAIN/'restricted-2/attempt-3/spec.json')  # original observation membership only
    density, heat = rows(E/'density.csv'), rows(E/'heat.csv')
    errors = {r['identity']:r['standard_error'] for r in rows(E/'conditional-standard-errors.csv')}
    coordinates = [dict(identity=c['identity'], unit=c['unit'], value=c['value'], bound_active=str(c['identity'] not in errors), conditional_standard_error=errors.get(c['identity'], '')) for c in fit['coordinates']]
    assert len(density)==210 and len(heat)==22 and len(coordinates)==16
    phase = rows(E/'phase-family.csv')
    paired = {name:{int(r['index']):r for r in phase if r['record']==('adopted #255 candidate' if name=='reported' else name)} for name in ('reported','comparison')}
    assert all(len(v)==162 for v in paired.values())
    assert not any(int(r['resolved_trials']) for r in paired['reported'].values())
    return fit, summary, document, fitted, spec, density, heat, coordinates, paired


def inventoried():
    """Check consumed numerical files against the retained adoption inventory."""
    inventory = {e['path']: e['sha256'] for e in load(BUNDLE / 'results/adoption-297/changed-files.json')}
    for path, digest in INPUTS.items():
        if path in inventory and not path.endswith('.py'):
            assert inventory[path] == digest, path
