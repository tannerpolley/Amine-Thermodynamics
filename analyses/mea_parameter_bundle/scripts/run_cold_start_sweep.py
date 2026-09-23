"""Cold-start sweep over every solved-pressure MEA request (fitted model), one wheel per process."""
import csv, hashlib, json, sys
from pathlib import Path
from time import perf_counter
W = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(W / 'analyses/mea_parameter_bundle/scripts'), str(W / 'src')]
import shared_evaluation as shared
label, wheel = sys.argv[1], Path(sys.argv[2])
shared.ENGINE_WHEEL = wheel
shared.ENGINE_WHEEL_SHA256 = hashlib.sha256(wheel.read_bytes()).hexdigest()
shared.verify_wheel()
shared.RUNS = Path('/tmp/mea-cold-start-sweep') / label
model = shared.epcsaft.Mixture(shared.load_parameters(shared.PARAMETERS))
reactions = shared._selected_reactions()
obs = [o for o in shared.load_state_packet()['observations'] if o['request']['pressure']['role'] == 'solved']
out = Path(sys.argv[3])
with out.open('w', newline='') as handle:
    w = csv.writer(handle)
    w.writerow(['label', 'wheel_sha256', 'identity', 'temperature_k', 'status', 'failure_code', 'iterations', 'evaluations', 'hessian_calls', 'wall_s', 'pressure_pa', 'co2_partial_pressure_pa'])
    for o in obs:
        t = perf_counter()
        r = shared.evaluate_state(model, o['request'], reactions, o['identity'], [], budget_s=60)
        ev = dict(r.get('evidence') or []); work = ev.get('iterations/evaluations/hessian_calls') or [None] * 3
        p = r['predictions']
        w.writerow([label, shared.ENGINE_WHEEL_SHA256, o['identity'], o['request']['temperature']['value'], r['status'], r['failure_code'], *work,
                    round(perf_counter() - t, 3), p.get('system-pressure'), p.get('co2-partial-pressure')])
        handle.flush()
        print(label, o['identity'], r['status'], work, round(perf_counter() - t, 2), flush=True)
