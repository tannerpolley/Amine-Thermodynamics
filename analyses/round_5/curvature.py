"""Charge-neutral composition curvature at fixed temperature and pressure (#433)."""
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

from amp import DECLARATION, ENDPOINTS, ExpandedPressure, ORIGINAL
from common import ROOT, RESULTS, fingerprints, save
from objective import BOUNDED, HIGH, LOW, MDEA, REPORTED
from part_ii import Route, calculation_declaration, epcsaft, eq, np, stable
from reaction_reference import AMP_RECORD, R
from scipy.linalg import null_space


def hessian(spec, T, P, x, rho, *, steps=False):
    x = np.asarray(x, dtype=float)
    face = x > 0
    z = np.array([spec.spec['element_formulas'][c]['charge'] for c in spec.model.component_ids])
    E = null_space(np.vstack([np.ones(sum(face)), z[face]]))
    if not E.shape[1]:
        raise ValueError('No independent normalized charge-neutral composition direction')
    model = spec.model
    base = model.state(T, rho=rho, x=x)
    anchor = model.state(T, P=P, x=x, phase='liquid')
    if anchor.density_branch_mismatch or abs(anchor.molar_density / base.molar_density - 1) > 1e-6:
        raise ValueError('Isobaric EOS liquid root differs from the equilibrated parent')
    cols = []
    for d in E.T:
        full = np.zeros(len(x))
        full[face] = d
        act = model.pressure_actions(T, P, x=x, phase='liquid', anchor=anchor,
                                     observables=[epcsaft.PropertyObservable.LogFugacityCoefficient],
                                     directions=[epcsaft.PressureActionDirection(composition=full)])
        matrix_column = np.asarray([q.action for q, active in zip(act.results, face, strict=True) if active], dtype=float)
        if not np.isfinite(matrix_column).all():
            raise ValueError('Engine did not return a finite fugacity action on the active species face')
        cols.append(E.T @ (d/x[face] + matrix_column))
    H = np.array(cols).T
    metric = E.T @ (E / x[face, None])
    factors = np.linalg.cholesky(metric)
    scaled = np.linalg.solve(factors, np.linalg.solve(factors, H).T).T
    eig, vectors = np.linalg.eigh((scaled + scaled.T) / 2)
    dx = np.zeros(len(x))
    dx[face] = E @ np.linalg.solve(factors.T, vectors[:, 0])
    condition = float(np.linalg.cond(metric))
    antisymmetry = np.max(abs(scaled - scaled.T))
    resolution = max(float(antisymmetry), np.finfo(float).eps * condition * max(1., abs(eig).max()))
    out = dict(eigenvalues=eig, minimum=eig[0], symmetry=antisymmetry, metric_condition=condition,
               sign='negative' if eig[0] < -resolution else 'positive' if eig[0] > resolution else 'undecided',
               minimum_direction=dx, face=[c for c, include in zip(model.component_ids, face, strict=True) if include],
               metric_error_estimate=resolution, rank=E.shape[1], x=x, density_mol_m3=rho)
    if steps:
        sweep = []
        xmax = min(x[dx != 0]/abs(dx[dx != 0]))
        def read(xi):
            state = model.state(T, P=P, x=xi, phase='liquid')
            mu = np.log(xi[face] * state.molar_density) + np.array(state.residual_chemical_potential_over_rt)[face]
            g = xi[face] @ (np.log(xi[face] * state.molar_density)-1) + state.residual_helmholtz + P/(R*T*state.molar_density)
            return mu, g
        g0 = read(x)[1]
        factors = (.1,.03,.01,.003,.001,.0003,.0001,.00003) if abs(eig[0]) < 1e-6 else (.1,.03,.01)
        for h in (xmax*f for f in factors):
            up, down = (read(x + sign*h*dx) for sign in (1, -1))
            sweep.append(dict(step=h, projected_mu_curvature=dx[face] @ (up[0]-down[0])/(2*h),
                              gibbs_curvature=(up[1]+down[1]-2*g0)/h**2))
        out['isobaric_step_sweep'] = sweep
    return out


def parent_curvature(spec, item, *, tpd=True):
    problem = item.problem
    T = problem.temperature.value
    row = dict(T_K=T, feed_mol=problem.feed.values, P_basis='bubble' if item.pressure_reference else 'imposed')
    try:
        if item.pressure_reference:
            bubble = eq.solve_equilibrium(spec.model, item.pressure_reference)
            row.update(bubble_message=bubble.message, bubble_Pa=bubble.pressure)
            if not bubble.requested_tolerance_met:
                raise ValueError(bubble.message)
            problem.pressure = type(problem.pressure).fixed(bubble.pressure)
            x, rho = bubble.phase_mole_fractions(0), bubble.molar_densities[0]
            closure = max(map(abs,bubble.residuals))
        else:
            parent = eq.solve_equilibrium(spec.model, problem)
            if not parent.requested_tolerance_met:
                raise ValueError(parent.message)
            x, rho = parent.phase_mole_fractions(0), parent.molar_densities[0]
            closure = max(map(abs,parent.residuals))
        P = problem.pressure.value
        row.update(P_Pa=P, max_abs_equilibrium_residual=closure)
        row.update(hessian(spec,T,P,x,rho))
        if tpd:
            if item.pressure_reference:
                parent = eq.solve_equilibrium(spec.model, problem)
                if not parent.requested_tolerance_met:
                    raise ValueError(parent.message)
            options = item.stability_options
            options.mode = type(options.mode).Full
            search = eq.stability_test(eq.compile_problem(spec.model, problem), parent, options)
            row['stability_trials'] = [dict(seed=t.seed, composition=t.composition, evidence=t.evidence,
                                           descent=t.resolved_descent, quantities=t.quantities) for t in search.trials]
            row['liquid_descent'] = any(t.resolved_descent and t.quantities.get('density_side') == 2 for t in search.trials)
            row['vapor_descent'] = any(t.resolved_descent and t.quantities.get('density_side') == 1 for t in search.trials)
    except (RuntimeError, ValueError, AttributeError, np.linalg.LinAlgError) as error:
        row['refusal'] = f'{type(error).__name__}: {error}'
    return row


def fitted_states(route, point):
    spec = route.bind(point)
    unique, rows = {}, []
    for r in spec.inputs['observations']['fitted']:
        requests = [(slot,dict(problem=r[slot])) for slot in ('problem','initial','final','bubble') if slot in r]
        if r['constructor'] == 'saturation_capped_addition_enthalpy':
            requests.append(('capped endpoint',dict(cap_record=r['identity'])))
        for slot, request in requests:
            observation = dict(identity=r['identity'], slot=slot, group=r['group'])
            try:
                item = route.stability_row(spec, request, 1.)
                signature = str(calculation_declaration([item.problem,item.pressure_reference]))
                entry = unique.setdefault(signature, dict(item=item, records=[]))
                entry['records'].append(observation)
            except (ValueError, RuntimeError) as error:
                rows.append(dict(observations=[observation], refusal=f'{type(error).__name__}: {error}'))
    for entry in unique.values():
        row = parent_curvature(spec, entry['item'])
        rows.append(dict(row, observations=entry['records'], state_type='loaded reactive' if
                         entry['item'].problem.reactions and entry['item'].problem.feed.values[list(spec.model.component_ids).index('carbon-dioxide')]>0
                         else 'unloaded or binary'))
    available = [r for r in rows if 'minimum' in r]
    for row in {id(r):r for r in [*sorted(available, key=lambda r:r['minimum'])[:1],
                                  *sorted(available, key=lambda r:abs(r['minimum']))[:1]]}.values():
        try:
            row.update(hessian(spec, row['T_K'], row['P_Pa'], row['x'], row['density_mol_m3'], steps=True))
        except (RuntimeError, ValueError, AttributeError, np.linalg.LinAlgError) as error:
            row['step_sweep_refusal'] = str(error)
    return rows


def calculate(work):
    started = monotonic()
    archive = stable.read(AMP_RECORD)
    route = Route(DECLARATION, work/'AMP')
    reported = stable.read(ENDPOINTS / 'main/parameters.json')
    spec = route.bind(reported)
    known = ROOT / 'analyses/mea_parameter_bundle/results/split-diagnosis-433/amp-hessian.json'
    controls = []
    for p, target in zip(archive['phases'], stable.read(known)[:3], strict=True):
        result = hessian(spec, archive['T_K'], archive['P_Pa'], p['x'], p['density_mol_m3'], steps=True)
        result['retained_minimum'] = target['eig'][0]
        result['difference'] = result['minimum']-target['eig'][0]
        controls.append(result)
    save('D/S14-hessian.json', dict(phases=controls, inputs=fingerprints(known, AMP_RECORD)), start=started)
    points = [(f'AMP-original-{label}', DECLARATION, ENDPOINTS / label / 'parameters.json', Route) for label in ORIGINAL]
    points += [(f'AMP-expanded-{label}', DECLARATION, RESULTS / f'A/expanded-{label}.json.gz', ExpandedPressure)
               for label in ('free','fixed')]
    points += [(f'MDEA-{label}', MDEA, p, Route) for label, p in
               [('low',LOW),('reported',REPORTED),('high',HIGH),('unbounded',BOUNDED/'fits/unbounded-2/endpoint.json')]]
    completed = []
    for name, declaration, p, kind in points:
        if monotonic()-started >= 1080:
            break
        tick = monotonic()
        point = stable.read(p)
        point = point['point'] if kind is ExpandedPressure else point
        try:
            rows = fitted_states(kind(declaration, work/name), point)
        except (ValueError, RuntimeError, AssertionError) as error:
            rows = [dict(refusal=f'{type(error).__name__}: {error}')]
        groups = defaultdict(list)
        for r in rows:
            groups[r.get('state_type','unknown')].append(r)
        summary = [dict(kind=k, count=len(rr), refused=sum('refusal' in r for r in rr), sign_counts={
            s:sum(r.get('sign')==s for r in rr) for s in ('positive','negative','undecided')},
                        minimum=min((r['minimum'] for r in rr if 'minimum' in r), default=None))
                   for k, rr in groups.items()]
        save(f'D/{name}.json.gz', dict(rows=rows, summary=summary, inputs=fingerprints(declaration,p)), start=tick)
        completed.append(name)
    save('D/fitted-timing.json', dict(projection_minutes=[3,9], completed=completed,
         skipped=[name for name, *_ in points if name not in completed]), start=started)


def near_zero_binary(work):
    started = monotonic()
    fitted = RESULTS/'D/MDEA-unbounded.json.gz'
    point_path = BOUNDED/'fits/unbounded-2/endpoint.json'
    spec = Route(MDEA,work).bind(stable.read(point_path))
    row = min((r for r in stable.read(fitted)['rows'] if 'minimum' in r),key=lambda q:abs(q['minimum']))
    verified = hessian(spec,row['T_K'],row['P_Pa'],row['x'],row['density_mol_m3'],steps=True)
    sweep = verified['isobaric_step_sweep']
    extrapolated = []
    for a,b in zip(sweep,sweep[1:]):
        ratio_squared = (b['step']/a['step'])**2
        extrapolated.append((b['projected_mu_curvature']-ratio_squared*a['projected_mu_curvature'])/(1-ratio_squared))
    save('D/MDEA-unbounded-near-zero.json',dict(T_K=row['T_K'],P_Pa=row['P_Pa'],
         observations=row['observations'],search=row.get('stability_trials'),hessian=verified,
         extrapolated_projected_mu_curvature=extrapolated,inputs=fingerprints(fitted,point_path,MDEA)),start=started)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--near-zero',action='store_true')
    args = parser.parse_args()
    with TemporaryDirectory() as directory:
        (near_zero_binary if args.near_zero else calculate)(Path(directory))
