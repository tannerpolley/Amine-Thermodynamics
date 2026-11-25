"""Replay the 30 wt% DEA two-liquid calculation at loading 0.50 mol/mol."""
from pathlib import Path
from tempfile import TemporaryDirectory

from _inputs import RESULTS, endpoint, fingerprint, r
from phases import fixed
from refit import P_REF, Route
from receivers import DEA

point = endpoint('DEA')
key = 'weiland-1998:43:problem'
retained = r.read(RESULTS / 'DEA/controls/A.json.gz')
assert retained['endpoint_fingerprint'] == fingerprint(point)
state = retained['rows'][key]
old = r.read(RESULTS.parents[1] / 'round_7/results/F/search-outcome.json.gz')
seed = next(a for row in old['classifications'] if row['key'] == key for a in row['attempts'] if a['confirmed'])
with TemporaryDirectory() as work:
    route = Route(DEA, Path(work), fixed_reference_pressure_pa=P_REF)
    replay = fixed(route, route.bind(point), state['state'], state['P_Pa'], {'pair': seed})
assert replay['physical_checks_pass']
assert all(rx['reference']['reference_pressure_pa'] == P_REF for rx in replay['declaration']['reactions'])
pair = next(a for a in replay['attempts'] if a['confirmed'])
expected = next(a for a in state['value']['attempts'] if a['confirmed'])
error = pair['numerical_error_over_RT_mol'] + expected['numerical_error_over_RT_mol']
assert abs(pair['Gibbs_decrease_over_RT_mol'] - expected['Gibbs_decrease_over_RT_mol']) <= error
for record in (pair, expected):
    record['daughters'] = sorted(zip(record['densities_mol_m3'], record['amounts_mol'], strict=True))
for (rho, n), (rho_ref, n_ref) in zip(pair['daughters'], expected['daughters'], strict=True):
    assert abs(rho-rho_ref) <= 0.005 and abs(n-n_ref) <= 0.0000005
    print(f'daughter density = {rho:.2f} mol/m^3, amount = {n:.6f} mol')
print(f"Gibbs decrease / RT = {pair['Gibbs_decrease_over_RT_mol']:.9f} mol")
