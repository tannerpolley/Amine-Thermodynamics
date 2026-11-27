"""Replay the 30 wt% DEA two-liquid calculation at loading 0.50 mol/mol."""
from _inputs import RESULTS, endpoint, fingerprint, read
from analyses.amines.dea import FIT_SETS
from analyses.amines.phase import coexistence, eq, gibbs, physical, stability_row

route, point = endpoint(FIT_SETS["reported"])
key = "weiland-1998:32:problem"
retained = read(RESULTS / "dea/reported/phase/DEA/screen/selected/declared/summary.json.gz")
assert retained["endpoint_fingerprint"] == fingerprint(point)
rows = {row["key"]: row for row in retained["classifications"]}
state = rows[key]
expected = next(a for a in state["attempts"] if a["confirmed"])
seed = next(a for a in rows[expected["seed_from"]]["attempts"] if a["confirmed"])
spec = route.bind(point)
parent = stability_row(route, spec, {"problem": key}, 1.0).problem
parent.pressure = type(parent.pressure).fixed(state["pressure_Pa"])
center = eq.solve_equilibrium(spec.model, parent)
assert center.requested_tolerance_met and physical(spec, parent, center)["physical_checks_pass"]
assert list(parent.feed.values) == state["feed_mol"] and center.temperature == state["temperature_K"]
assert all(rx.reference.reference_pressure_pa == route.fixed_reference_pressure_pa for rx in parent.reactions)
parent_g = gibbs(eq.compile_problem(spec.model, parent), center)
pair = coexistence(spec, parent, parent_g, list(zip(seed["phases"], seed["packings"], strict=True)))
assert pair["confirmed"]
error = pair["numerical_error_over_RT_mol"] + expected["numerical_error_over_RT_mol"]
assert abs(pair["Gibbs_decrease_over_RT_mol"] - expected["Gibbs_decrease_over_RT_mol"]) <= error
for record in (pair, expected):
    record["daughters"] = sorted(zip(record["densities_mol_m3"], record["amounts_mol"], strict=True))
for (rho, n), (rho_ref, n_ref) in zip(pair["daughters"], expected["daughters"], strict=True):
    assert abs(rho - rho_ref) <= 0.005 and abs(n - n_ref) <= 0.0000005
    print(f"daughter density = {rho:.2f} mol/m^3, amount = {n:.6f} mol")
print(f"Gibbs decrease / RT = {pair['Gibbs_decrease_over_RT_mol']:.9f} mol")
