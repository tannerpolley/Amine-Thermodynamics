"""Fixed-point 142-target identification for the serialized working record (#107)."""
from pathlib import Path
import sys
import json
import resource
import csv
import numpy as np

b = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(b / 'model-d'))
import fit  # noqa: E402
from compare import in_working_objective  # noqa: E402

s = fit.probe.shared
regression = fit.refit.regression
out = b / 'results'
mapping = s.parameter_mapping()
candidate = s.parameter_mapping(b / 'model-d/born-form-diagnosis/p5conv-a-11-diagnostic-parameters.json')
assert s.parameter_values(candidate) == s.parameter_values(mapping)
assert candidate['topology'] == mapping['topology'] and candidate['model_families'] == mapping['model_families']
request = s.load_state_packet()['observations'][0]['request']
assert s._engine_reaction_records(request, s.reaction_values(candidate)) == s._engine_reaction_records(request, s._selected_reactions())
p = s.load_parameters()
ids = list(fit.S1)
coordinates = [regression.coordinate(p, 'k_ij_reciprocal_temperature_slope' if i.endswith(fit.SLOPE) else 'k_ij', tuple(i.split('/')[1:3]), origin=s.parameter_values(mapping)[i], scale=10 if i.endswith(fit.SLOPE) else .01, bounds=bounds) for i, bounds in fit.S1.items()]
packet = {r['identity']: r for r in map(json.loads, (out / 'promotion-107-packet.jsonl').open())}
rows = []
for o in fit.probe.OBSERVATIONS:
    r = packet[o['identity']]
    if not any(in_working_objective(r, t) for t in o['targets']):
        continue
    liq = r['liquid']
    anchor = s.Anchor(round(r['T']-273.15), float(r['feed'][0]), float(liq['pressure_pa']), tuple(liq['mole_fractions']), float(liq['molar_volume_m3_per_mol']))
    prob = s._problem_from_request(s.corrected_request(o['request'], s.reaction_values(mapping)), anchor)
    rows.extend(row for row in fit.refit.observations(p, o, prob, 80) if any(t['identity'] == row[0] and in_working_objective(r, t) for t in o['targets']))
assert len(rows) == 142
controls = regression.FitControls()
controls.maximum_iterations = 1  # Native initial residual/Jacobian only; no optimizer update.
controls.maximum_elapsed_time_seconds = 1700.
result = regression.fit(p, coordinates, [r[1] for r in rows], weights=[r[2] for r in rows], controls=controls)
assert result.iterations == 1 and list(result.physical) == [s.parameter_values(mapping)[i] for i in ids]
assert all(status == regression.ObservationStatus.Available for status in result.statuses)
J = np.array(result.optimizer_jacobian).reshape(142, 5) / np.array([c.scale for c in coordinates])
r = np.array(result.weighted_residuals)
assert abs(.5*r@r - 32.9918972612169) <= 1e-8
summary = dict(parameter_sha256=s.sha256(s.PARAMETERS), engine_wheel_sha256=s.ENGINE_WHEEL_SHA256, targets=142, coordinates=ids, method='native initial exact physical Jacobian; zero optimizer updates', physical_singular_values=np.linalg.svd(J, compute_uv=False).tolist(), column_normalized_singular_values=np.linalg.svd(J/np.linalg.norm(J, axis=0), compute_uv=False).tolist(), cost=float(.5*r@r), cost_gradient=dict(zip(ids, J.T@r)), active_bound='pair/bicarbonate-anion/water/k_ij = +0.5', covariance='not reported at the active bound', memory_limit_bytes=resource.getrlimit(resource.RLIMIT_AS))
s.write_json(out / 'promotion-107-identification.json', s._jsonable(summary))
with (out / 'promotion-107-jacobian.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, ['target', 'weighted_residual', *ids], lineterminator='\n')
    w.writeheader()
    w.writerows(dict(target=row[0], weighted_residual=float(residual), **dict(zip(ids, values))) for row, residual, values in zip(rows, r, J, strict=True))
