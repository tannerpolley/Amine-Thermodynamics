"""Replay the worked MEA heat and heat capacity at 313.15 K."""
from pathlib import Path
from tempfile import TemporaryDirectory

from _inputs import ROOT, STUDY, endpoint, fingerprint, r
from property_replays import P_REF, fixed_native_reference, save
from reference_states_428 import mea

point = endpoint('MEA')
retained = r.read(STUDY / 'results/display-replays/caloric-and-species.json.gz')
assert retained['endpoint_fingerprint'] == fingerprint(point)
with TemporaryDirectory(dir=ROOT / 'build') as work:
    mapping = Path(work) / 'parameters.json'
    save(mapping, point['parameters'])
    with fixed_native_reference():
        replay = mea(mapping, reaction_reference_pressure_pa=P_REF)
assert all(replay['checks'].values()), replay['checks']
expected = retained['reference_state']
for key, places in [('heat_kJ_mol', 3), ('cp_J_mol_K', 3)]:
    assert abs(replay[key] - expected[key]) <= 0.5 * 10**-places, (key, replay[key], expected[key])
    print(f'{key} = {replay[key]:.{places}f}')
