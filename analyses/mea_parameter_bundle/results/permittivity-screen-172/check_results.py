"""Check unchanged inputs, numerical reference replay and complete retained rows."""
import copy
import hashlib
import math
import permittivity_probe as s

SELECTED_SHA = '66ff7715958e9d22e77bd129faf7f67822204e3285b50993bf3f67d72c3b9778'
assert hashlib.sha256(s.s.PARAMETERS.read_bytes()).hexdigest() == SELECTED_SHA


def remaining(record):
    value = copy.deepcopy(record)
    for key in ('document_id', 'purpose', 'sources'):
        value.pop(key, None)
    value['model_families'] = [f for f in value['model_families'] if f['kind'] != 'permittivity']
    value['correlations'] = [c for c in value['correlations'] if c['family'] != 'relative_permittivity']
    for component in value['components']:
        component['coefficients'] = [r for r in component['coefficients'] if r['family'] not in
            ('relative_permittivity', 'dielectric_volume', 'dielectric_temperature')]
    return value


for name, record in s.VARIANTS.items():
    assert remaining(record) == remaining(s.CURRENT), name
    if name == 'baseline':
        continue
    assert record['sources'][:-1] == s.CURRENT['sources'], name
    model = s.mixture(record)
    anchor = model.state(298.15, P=101325., x=[0., 1., 0., 0., 0., 0., 0., 0., 0.], phase='liquid')
    assert abs(anchor.bulk_relative_permittivity - 30.45) < 1e-11, name
    # The tolerance resolves only floating-point evaluation of the imposed algebraic anchor.
    if name.endswith('epsilon-1.55'):
        anchor = model.state(298.15, rho=20000., x=[1., 0., 0., 0., 0., 0., 0., 0., 0.])
        assert abs(anchor.bulk_relative_permittivity - 1.55) < 1e-11, name

rows = s.read(s.OUT/'targets.json')
assert len(rows) == 7*163 and len({(r['variant'], r['target']) for r in rows}) == len(rows)
for name in s.VARIANTS:
    part = [r for r in rows if r['variant'] == name]
    assert all(r['status'] == 'Available' and math.isfinite(r['predicted']) for r in part)
    assert sum(r['target'].endswith('-pco2') for r in part) == 47
    assert sum(r['source'] == 'Vinjarapu2024' for r in part) == 8
    assert sum(r['source'] == 'Arcis2011' for r in part) == 14
    assert len(part)-47-8-14 == 94

family = s.read(s.OUT/'flash-family.json')
assert len(family) == 2*7*73
assert len({(r['basis'], r['variant'], r['index']) for r in family}) == len(family)
for r in family:
    if r['accepted']:
        assert r['residual'] <= 1e-10 and all(v > 0. for v in r['amounts'])
        assert all(v > 0. and math.isfinite(v) for v in r['molar_densities'])

falsifier = s.read(s.OUT/'falsifier.json')
reference = s.read(s.OUT/'inputs/falsifier-physical.json')['row']
control = next(r for r in falsifier if r['basis'] == 'engine-case7' and r['variant'] == 'baseline' and r['state'] == 'retained-physical')
# Same 1e-8 relative replay tolerance used by the repository's fixed-record evaluator.
assert abs(control['G_over_RT']/float(reference['objective']) - 1.) <= 1e-8
for r in falsifier:
    if r['variant'] != 'baseline' and r['state'] == 'gas-composition-vapor-root':
        assert r['stable_root_count'] == 1 and r['molar_density_mol_m3'] > 50000.
print('CHECKED: unchanged non-dielectric inputs; six imposed anchors; 1141 target predictions; 1022 cold flash rows; retained Engine Gibbs reference', flush=True)
