"""Replay the C1 pressure and temperature derivatives at one MEA bubble state."""
from _inputs import RESULTS, endpoint, fingerprint, read
from analyses.amines.mea import FIT_SETS
from analyses.amines.properties import worked_state

route, point = endpoint(FIT_SETS['reported'])
retained = read(RESULTS / 'shared/comparisons/properties/derivatives/selected-MEA.json.gz')
assert retained['endpoint_fingerprint'] == fingerprint(point)
spec = route.bind(point)
replay = worked_state(spec, spec.model, spec.thermal, retained['observation'], retained['apparent_amine_feed_mol'])
assert replay['center']['admitted']
assert abs(replay['P_Pa'] - retained['P_Pa']) <= replay['P_Pa'] * 1e-10
step, expected = replay['steps'][1], retained['steps'][1]
assert step['volume_admitted'] and step['enthalpy_admitted']
for error, resolution, unit in [
    ('signed_volume_error_m3', 'volume_arithmetic_error_m3', 'm^3'),
    ('eq12_minus_Gibbs_Helmholtz_J', 'caloric_arithmetic_error_J', 'J'),
]:
    assert abs(step[error]) <= step[resolution], dict(step=step['step_K'], error=step[error])
    assert abs(step[error] - expected[error]) <= step[resolution] + expected[resolution]
    print(f'{error} = {step[error]:+.4e} {unit} (resolution {step[resolution]:.4e} {unit})')
assert abs(replay['center']['volume_m3'] - retained['center']['volume_m3']) <= expected['volume_arithmetic_error_m3']
assert abs(step['Gibbs_Helmholtz_H_J'] - expected['Gibbs_Helmholtz_H_J']) <= (
    step['caloric_arithmetic_error_J'] + expected['caloric_arithmetic_error_J']
)
print(f"liquid volume = {replay['center']['volume_m3']:.9g} m^3")
print(f"Gibbs-Helmholtz enthalpy = {step['Gibbs_Helmholtz_H_J']:.4f} J")
