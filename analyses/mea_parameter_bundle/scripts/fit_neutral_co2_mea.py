"""Amendment 4 neutral CO2-MEA fit (starts A/B), endpoint checks and cold replay (#170)."""
import csv, math, sys, time
from pathlib import Path
import numpy as np
import fit_campaign as campaign
import fit_observations as owner
root = Path('analyses/mea_parameter_bundle/results/joint-recalibration-170')
out, mode, started, cpu = Path(sys.argv[1]), sys.argv[2], time.monotonic(), campaign.cpu_seconds()
rows = list(csv.DictReader(open('data/reference/MEA/physical_solubility/CO2_physical_from_N2O.csv')))
factor = {r['id']: r['correction_factor_on_H'] for r in campaign.load(sys.argv[3])['rows']} if len(sys.argv) > 3 else {}  # B1 source-to-model target transfer
pair = ('pair/carbon-dioxide/monoethanolamine/k_ij', 'pair/carbon-dioxide/monoethanolamine/k_ij/reciprocal_temperature_slope')
def neutral(branch, values):
    mapping = campaign.load(root/f'amendment-2/route2b/{branch}/start-parameters.json')
    shared = owner.s.parameter_values(campaign.load(root/'stage2/co2-water/slope/co2-water/B/parameters.json'))
    mapping = owner.s.with_parameter_values(mapping, {k: v for k, v in shared.items() if k in owner.s.parameter_values(mapping)} | dict(zip(pair, values)))
    mapping['topology']['no_cross_association'] = [dict(component_id_a='carbon-dioxide', component_id_b='monoethanolamine', provenance=dict(source_id=mapping['document_id'], locator=f'route2b/{branch}/start-parameters.json topology.edges: no carbon-dioxide/monoethanolamine edge (#191)'))]
    return mapping
def problem(T, w, epsilon=1e-6):  # endpoint sentinel: 1e-5 -> 1e-6 changes Hx by 1.13e-4 at 360.25 K
    x = w/0.06108/(w/0.06108+(1-w)/0.01801528)
    return owner.eq.Problem(T=T, P=owner.eq.Free(10000.), feed=owner.eq.Amounts({'carbon-dioxide': epsilon, 'monoethanolamine': (1-epsilon)*x, 'water': (1-epsilon)*(1-x)}), phases=[owner.eq.Phase(n, kind=k, support=['carbon-dioxide', 'monoethanolamine', 'water'], **a) for n, k, a in (('L', 'liquid', {}), ('V', 'vapor', dict(amount=owner.eq.Pinned(0.))))], reactions=(), row_tolerance=1e-10)
def evaluate(mapping, values, start=(0., 0.)):
    params = owner.epcsaft.Parameters.from_mapping(mapping)
    coords = [owner.reg.coordinate(params, [(f, ('carbon-dioxide', 'monoethanolamine'), 1.)], origin=v, scale=s, bounds=b) for f, v, s, b in zip(('k_ij', 'k_ij_reciprocal_temperature_slope'), start, (0.01, 10.), ((-0.5, 0.5), (-500., 500.)))]
    items = [owner.reg.observation(params, 'partial_pressure', problem(float(r['temperature_K']), float(r['mea_mass_fraction'])), observed=1e-6*float(r['H_CO2_primary_mole_fraction_Pa'] or r['H_CO2_physical_mole_fraction_Pa'])*factor.get(r['record_id'], 1.), form='log_ratio', phase='V', species=['carbon-dioxide']) for r in rows]
    v = owner.reg.differentiate(params, coords, items, optimizer=[(a-b)/s for a, b, s in zip(values, start, (0.01, 10.))])
    w = np.array([float(r['neutral_log_ratio_weight']) for r in rows])
    J = np.array(v.residual_optimizer_gradient).reshape(len(rows), 2)[w > 0]*np.sqrt(w[w > 0, None])
    sv = np.linalg.svd(J, compute_uv=False)
    error = [p/i.observed-1 for p, i in zip(v.predictions, items)]
    return params, coords, items, dict(predictions=list(v.predictions), statuses=[s.name for s in v.statuses], relative_H_error=error, singular_values=sv.tolist(), rank=int(sum(sv > sv[0]*1e-14)), condition=float(sv[0]/sv[-1]), hartono_mean_abs_error=float(np.mean(np.abs(error[:7]))), hartono_max_abs_error=float(np.max(np.abs(error[:7]))), xu_mean_abs_error=float(np.mean(np.abs(error[7:]))), xu_max_abs_error=float(np.max(np.abs(error[7:]))))
if mode == 'fit':
    campaign.write(out/'inputs.json', campaign.verify(dict(inputs=[dict(path=p, sha256=h) for p, h in (('data/reference/MEA/physical_solubility/CO2_physical_from_N2O.csv', '711813f70cad20fb571e63e90e1d740f7d8ea3099ef3f84ee475020851697422'), (str(root/'stage2/co2-water/slope/co2-water/B/parameters.json'), 'b1ec1ddc22abe5ced8d08116fc91a7b3da1361864db1b34c33dda121b642a5e2'), (str(root/'amendment-2/route2b/larger-dV/start-parameters.json'), 'aee26a2dc1149854ff0840d4bd5bfac58ec423aac1cfec7b870b1ccbbbc2d202'), (str(root/'amendment-2/route2b/smaller-dV/start-parameters.json'), 'f9a9d6ea7a46e900721eefbf8eb77a94a21fadfcee89ab44e43774b6ab6a3815'))], engine=dict(wheel_path='tmp/amendment-4-21e761c3/wheel/epcsaft-0.2.0.dev0-cp313-cp313-manylinux_2_39_x86_64.whl', wheel_sha256='d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357', packages=dict(epcsaft='0.2.0.dev0', numpy='2.5.4', scipy='1.18.1')))))
    campaign.write(out/'target-factors.json', factor)
    for label, start in (('A', (0., 0.)), ('B', (0.10, 100.))):
        params, coords, items, at_start = evaluate(neutral('larger-dV', start), start, start)
        clock = time.monotonic()
        v = owner.reg.fit(params, coords, items[:7], weights=[float(r['neutral_log_ratio_weight']) for r in rows[:7]], controls=owner.reg.FitControls(maximum_iterations=100, function_tolerance=1e-6, parameter_tolerance=1e-10, gradient_tolerance=1e-8, maximum_elapsed_time_seconds=60, workers=7), singular_vectors=True)
        raw = {k: owner.s._jsonable(getattr(v, k)) for k in ('status', 'message', 'usable', 'initial_cost', 'final_cost', 'physical', 'optimizer', 'predictions', 'weighted_residuals', 'optimizer_jacobian', 'iterations', 'iteration_costs', 'residual_evaluations', 'jacobian_evaluations')}
        raw.update(native_wall_s=time.monotonic()-clock, covariance={k: owner.s._jsonable(getattr(v.covariance, k)) for k in ('status', 'rank', 'singular_values', 'physical', 'active_bounds', 'projected_gradient_norm', 'right_vectors')})
        endpoint = list(v.physical)
        campaign.write(out/f'{label}/native.json', raw)
        campaign.write(out/f'{label}/parameters.json', neutral('larger-dV', endpoint))
        campaign.write(out/f'{label}/evaluation.json', dict(start=at_start, endpoint={b: evaluate(neutral(b, endpoint), endpoint)[3] for b in ('larger-dV', 'smaller-dV')}))
else:  # cold replay of each retained endpoint document in a fresh process
    result = {}
    for label in ('A', 'B'):
        mapping = campaign.load(out/f'{label}/parameters.json')
        values = [owner.s.parameter_values(mapping)[k] for k in pair]
        retained = campaign.load(out/f'{label}/evaluation.json')['endpoint']['larger-dV']['predictions']
        replay = evaluate(mapping, values)[3]['predictions']
        result[label] = dict(values=values, maximum_relative_difference=max(abs(a/b-1) for a, b in zip(replay, retained)))
    campaign.write(out/'cold-replay.json', result)
    model = owner.epcsaft.Mixture(owner.epcsaft.Parameters.from_mapping(campaign.load(out/'A/parameters.json')))
    n, i, sentinel = len(model.component_ids), model.component_ids.index('carbon-dioxide'), []
    for T in (298.35, 360.25):  # endpoint dilution sentinel (addendum prerequisite at the nonzero pair)
        for epsilon in (1e-5, 1e-6, 1e-7):
            d = problem(T, 0.3, epsilon); st = owner.eq.solve_equilibrium(model, d); xs = list(st.mole_fractions)
            sentinel.append(dict(T=T, epsilon=epsilon, success=st.success, requested_tolerance_met=st.requested_tolerance_met, message=st.message, pressure_Pa=list(st.pressure), molar_densities=list(st.molar_densities), mole_fractions=xs, Hx_Pa=xs[n+i]*st.pressure[0]/xs[i], raw_residual_max=max(map(abs, owner.eq.compile_problem(model, d).evaluate(st.coordinates).values)), dP_drho_Pa_m3_mol=[model.state(T, rho=r, x=xs[k*n:(k+1)*n]).pressure_density_derivative for k, r in enumerate(st.molar_densities)]))
    campaign.write(out/'endpoint-sentinel.json', sentinel)
campaign.write(out/f'timing-{mode}.json', dict(cpu_s=campaign.cpu_seconds()-cpu, wall_s=time.monotonic()-started))
