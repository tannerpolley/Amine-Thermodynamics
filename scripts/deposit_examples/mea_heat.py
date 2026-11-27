"""Replay the worked MEA heat and heat capacity at 313.15 K."""
from _inputs import RESULTS, endpoint, fingerprint, read
from analyses.amines.mea import FIT_SETS
from analyses.amines.properties import worked_calorimetry

route, point = endpoint(FIT_SETS["reported"])
retained = read(RESULTS / "shared/comparisons/properties/display-replays/caloric-and-species.json.gz")
assert retained["endpoint_fingerprint"] == fingerprint(point)
expected = retained["reference_state"]
replay = worked_calorimetry(route.bind(point), expected)
for key, places in [("heat_kJ_mol", 3), ("cp_J_mol_K", 3)]:
    assert abs(replay[key] - expected[key]) <= 0.5 * 10**-places, (key, replay[key], expected[key])
    print(f"{key} = {replay[key]:.{places}f}")
fine = replay["cp_stencil_J_mol_K"][-1]
assert abs(replay["cp_J_mol_K"] - fine) <= abs(expected["cp_minus_fine_J_mol_K"]) + 0.5e-3
