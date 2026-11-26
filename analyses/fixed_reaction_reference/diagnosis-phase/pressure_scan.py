"""Read pressure over consecutive representable densities at the four #441 refusals."""
from hashlib import sha256
from time import monotonic

from refit import OUT, a, epcsaft, np, put, r
from phase_replays import screen_declarations

ROOT = 'MEA/screen/rebuild-441/parent-closure'
CASES = {
    'MEA/grid': {'census|None|318.15|1e-05|1.05': 151},
    'DEA/declared': {'Cai:9:problem': 18},
    'AMP_free/native': {'kundu-2003:0:problem': 11, 'hartono-2013-P:0:problem': 3},
}
RADIUS = 200


def scan(model, problem, T, P, phase):
    start = monotonic()
    x = phase['x']
    rho = phase.get('original_density_mol_m3',phase['density_mol_m3'])
    state = model.state(T,rho=rho,x=x)
    tol = problem.row_tolerance
    slope = state.pressure_density_derivative
    target = rho + (P-state.pressure)/slope
    assert (state.pressure-P)==phase.get('original_pressure_residual_Pa',phase['pressure_residual_Pa'])
    ulp = np.spacing(target)
    native_offset = int((rho-target)/ulp)
    densities = [target]
    for side in (-np.inf,np.inf):
        value = target
        for _ in range(RADIUS):
            value = float(np.nextafter(value,side))
            densities.append(value)
    densities = sorted(densities)
    offsets = np.arange(-RADIUS,RADIUS+1)
    assert np.array_equal((np.asarray(densities)-target)/ulp,offsets)
    pressure = np.array([model.state(T,rho=v,x=x).pressure for v in densities])
    errors = (pressure-P)/P
    fitted_slope, intercept = np.polyfit(offsets,errors,1)
    noise = errors - (fitted_slope*offsets + intercept)
    best = int(np.argmin(abs(errors)))
    passes = np.flatnonzero(abs(errors)<=tol)
    prior_window = (abs(offsets)<=8)|(abs(offsets-native_offset)<=8)
    changes = np.flatnonzero(errors[:-1]*errors[1:]<0)
    support = np.asarray(x)>0
    reaction_support = [np.asarray(q.stoichiometry)!=0 for q in problem.reactions]
    active = [j for j,mask in enumerate(reaction_support) if not np.any(mask&~support)]
    checks = []
    for i in sorted({RADIUS,best,*[int(j) for j in changes[:3]],*[int(j)+1 for j in changes[:3]]}):
        density = densities[i]
        reads = [model.state(T,rho=density,x=x).pressure for _ in range(5)]
        derived = model.state(T,rho=density,x=x,derived_properties=True)
        batch, = model.states([T],rho=[density],x=x,derived_properties=True).pressure
        checks.append(dict(offset_ULP=int(offsets[i]),density_mol_m3=density,scalar_pressures_Pa=reads,
                           derived_pressure_Pa=derived.pressure,batch_derived_pressure_Pa=batch,
                           rho_RT_Z_Pa=density*epcsaft.GAS_CONSTANT_J_PER_MOL_K*T*derived.compressibility_factor,
                           pressure_density_derivative_Pa_m3_mol=derived.pressure_density_derivative))
    return dict(T_K=T,P_Pa=P,x=x,component_ids=list(model.component_ids),tolerance=tol,
                native_density_mol_m3=rho,newton_density_mol_m3=target,native_offset_ULP=native_offset,
                Z=P/(rho*epcsaft.GAS_CONSTANT_J_PER_MOL_K*T),density_ULP_mol_m3=ulp,
                analytic_step_per_ULP=slope*ulp/P,fitted_step_per_ULP=fitted_slope,
                local_fit_scatter_RMS=np.sqrt(np.mean(noise**2)),local_fit_scatter_max=np.max(abs(noise)),
                local_fit_scatter_peak_to_peak=np.ptp(noise),
                best_abs_relative_pressure_error=abs(errors[best]),best_offset_ULP=int(offsets[best]),
                minimum_in_prior_window=min(abs(errors[prior_window])),
                passing_offsets_ULP=offsets[passes].tolist(),
                adjacent_sign_changes_ULP=[[int(offsets[i]),int(offsets[i+1])] for i in changes],
                densities_mol_m3=densities,relative_pressure_errors=errors.tolist(),
                direct_readbacks=checks,active_reaction_indices=active,
                zero_components=[c for c,v in zip(model.component_ids,x,strict=True) if v==0],
                seconds=monotonic()-start)


def main():
    a.study.reuse.bind_wheel()
    r.verify()
    records={}
    for lane, cases in CASES.items():
        point,route,pool,*_=screen_declarations(lane)
        spec=route.bind(point)
        states={state['key']:state for state,_ in pool}
        for key,index in cases.items():
            source=f'{ROOT}/{lane}/{index}.json.gz'
            row=next(q for q in r.read(OUT/source)['rows'] if q['key']==key)
            problem=route.stability_row(spec,states[key],1.).problem
            scans={}
            for phase_step in ('initial_parent','parent'):
                phase, = row[phase_step]['phases']
                result=scan(spec.model,problem,row['T_K'],row['P_Pa'],phase)
                scans[phase_step]=result
                print(lane,key,phase_step, {k:result[k] for k in (
                    'Z','best_abs_relative_pressure_error','best_offset_ULP','minimum_in_prior_window',
                    'analytic_step_per_ULP','fitted_step_per_ULP','local_fit_scatter_RMS','local_fit_scatter_max',
                    'passing_offsets_ULP','adjacent_sign_changes_ULP','active_reaction_indices','seconds')},flush=True)
            records[key]=dict(lane=lane,source=source,source_sha256=sha256((OUT/source).read_bytes()).hexdigest(),scans=scans)
    put(f'{ROOT}/pressure-scan.json.gz',dict(wheel=r.SHA,engine='05e94210',radius_ULP=RADIUS,records=records))


if __name__=='__main__':
    main()
