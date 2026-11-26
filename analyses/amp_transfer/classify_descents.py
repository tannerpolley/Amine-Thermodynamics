"""Classify AMP pressure roots and attempt two-liquid coexistence for #404 descents."""
import math
import time

from part_ii import eq, jsonable, reg, stable

# Engine 05e94210 phase_stability.cpp, as retained in #344's classification record.
DENSITY_WINDOW = math.log(1.01)
COINCIDENCE = 1e-6
ERROR_TERMS = ('association_energy_estimate_over_rt',
               'feasibility_estimate_over_rt','summation_estimate_over_rt')


def pressure_roots(model, T, P, x, rho):
    checks = []
    for branch in ('liquid','vapor'):
        try:
            state = model.state(T, P=P, x=x, phase=branch)
            density, residual = state.molar_density, state.pressure-P
            checks.append(dict(requested=branch, returned=state.returned_density_branch.name.lower(), density=density,
                               T_K=T,P_Pa=P,log_density_distance=abs(math.log(density/rho)),
                               relative_pressure_residual=abs(residual)/P,pressure_residual_Pa=residual))
        except Exception as error:
            checks.append(dict(requested=branch, error=str(error)))
    return checks


def matched(checks, tolerance, density=None, *, T=None, P=None):
    from reference_states_428 import scaled_pressure_error

    def pressure_passes(root):
        temperature, pressure = root.get('T_K',T),root.get('P_Pa',P)
        if temperature is None or pressure is None:
            return False
        residual = root.get('pressure_residual_Pa',root['relative_pressure_residual']*pressure)
        return scaled_pressure_error(residual,root['density'],temperature)<=tolerance

    return [r for r in checks if 'density' in r and
            (r.get('log_density_distance',math.inf) if density is None else
             abs(math.log(r['density']/density)))<=DENSITY_WINDOW and pressure_passes(r)]


def distinct_phases(compositions, densities):
    return (max(abs(a-b) for a,b in zip(*compositions,strict=True))>COINCIDENCE or
            abs(math.log(densities[0]/densities[1]))>COINCIDENCE)


def gibbs(compiled, result, report=None):
    if report is None:
        report = eq.stability_test(compiled, result)
    phases = jsonable(report.present_phases)
    assert len(result.amounts)==len(phases) and phases
    return (math.fsum(n*q['g_over_rt'] for n,q in zip(result.amounts,phases,strict=True)),
            math.fsum(n*q[k] for n,q in zip(result.amounts,phases,strict=True) for k in ERROR_TERMS))


def coexistence(spec, parent, parent_g, guesses, *, inspect=None, start=None):
    compiled = eq.compile_problem(spec.model,parent)
    support = [i for i in range(len(spec.parameters.component_ids)) if i not in compiled.removed_species]
    phases = []
    for i,(x,packing) in enumerate(guesses):
        phase = type(parent.phases[0])()
        phase.name, phase.kind, phase.support_declared = f'L{i+1}', parent.phases[0].kind, True
        phase.support, phase.composition_guess, phase.packing_guess = support, [x[j] for j in support], packing
        phases.append(phase)
    original = parent.phases
    parent.phases = phases
    try:
        compiled = eq.compile_problem(spec.model,parent)
        result = eq.solve_equilibrium(spec.model,parent,start)
    finally:
        parent.phases = original
    out = dict(message=result.message, requested_tolerance_met=result.requested_tolerance_met,
               amounts_mol=list(result.amounts))
    if inspect is not None:
        out["diagnostics"] = inspect(compiled, result)
    if not result.requested_tolerance_met or len(result.amounts)!=2 or min(result.amounts)<=0:
        return dict(out, confirmed=False)
    diagnostics = out.get('diagnostics') or {}
    if 'physical_checks_pass' not in diagnostics:
        from round_3.phases import physical

        diagnostics.update(physical(spec,parent,result))
        out['diagnostics'] = diagnostics
    phases = [list(result.phase_mole_fractions(j)) for j in range(2)]
    densities = list(result.molar_densities)
    distinct = distinct_phases(phases,densities)
    report = eq.stability_test(compiled,result)
    roots = [pressure_roots(spec.model,result.temperature,result.pressure,x,rho)
             for x,rho in zip(phases,densities,strict=True)]
    liquid = all(any(r['returned']=='liquid' for r in matched(check,parent.row_tolerance)) for check in roots)
    g, error = gibbs(compiled,result,report)
    comparison = {} if parent_g is None else dict(Gibbs_decrease_over_RT_mol=parent_g[0]-g)
    estimated_error = error if parent_g is None else parent_g[1]+error
    return dict(out, confirmed=diagnostics['physical_checks_pass'] and distinct and liquid and comparison.get('Gibbs_decrease_over_RT_mol',-math.inf)>estimated_error,
                distinct=distinct, split_Gibbs_over_RT_mol=g, split_only=parent_g is None and distinct and liquid, **comparison,
                numerical_error_over_RT_mol=estimated_error, phases=phases,
                Gibbs_sum_over_RT_mol=g, objective_over_RT_mol=result.objective, residuals=list(result.residuals),
                densities_mol_m3=densities, packings=list(result.packing_fractions),
                max_abs_equilibrium_residual=max(map(abs,result.residuals)), roots=roots)


def classify(route, point, rows, states):
    from round_3.phases import liquid_vapor, physical

    spec = route.bind(point)
    by_key = {s['key']:s for s in states}
    results, unresolved, solutions = [], [], {}

    def inspect(compiled, result):
        last[:] = [result]
        if result.requested_tolerance_met and len(result.amounts)==2 and min(result.amounts)>0:
            return physical(spec,parent,result)

    last = []
    for row in rows:
        if not stable.descent(row):
            continue
        entry = dict(key=row['key'], native_branch=row['native_branch'],
                     supplied_branch=row['supplied_branch'], attempts=[])
        results.append(entry)
        try:
            item = route.stability_row(spec, by_key[row['key']], 1.)
            prediction = reg.predict(spec.model,item)
            parent = item.problem
            if prediction.pressure_reference is not None:
                parent.pressure = type(parent.pressure).fixed(prediction.pressure_reference.value*item.pressure_ratio)
            central = eq.solve_equilibrium(spec.model,parent)
            assert central.requested_tolerance_met, central.message
            T,P = central.temperature,central.pressure
            parent_x = list(central.phase_mole_fractions(0))
            parent_roots = pressure_roots(spec.model,T,P,parent_x,central.molar_densities[0])
            entry.update(temperature_K=T, pressure_Pa=P, feed_mol=list(parent.feed.values),
                         parent_roots=parent_roots, outside_ranges=route.marks(T,parent),
                         row_tolerance=parent.row_tolerance, parent=physical(spec,parent,central))
            compiled = eq.compile_problem(spec.model,parent)
            assert entry['parent']['physical_checks_pass'], 'Parent misses scaled closure'
            report = eq.stability_test(compiled,central,item.stability_options)
            parent_g = gibbs(compiled,central,report)
            primary = (parent_x,central.packing_fractions[0])
            entry['liquid_vapor'] = liquid_vapor(spec,route,parent,primary,parent_g)
            guesses, supplied = [], []
            for witness in row.get('supplied_trial_evidence',[]):
                if not stable.supplied_negative(witness):
                    continue
                phase, q = witness['phase'],witness['quantities']
                x = phase['composition']
                roots = pressure_roots(spec.model,T,P,x,q['molar_density_mol_m3'])
                candidates = matched(roots,parent.row_tolerance)
                evidence = dict(witness=witness,roots=roots)
                supplied.append(evidence)
                if candidates:
                    root = min(candidates,key=lambda r:r['log_density_distance'])
                    packing = q['packing_fraction']*root['density']/q['molar_density_mol_m3']
                    reclosed, _, _, _ = stable._applicable(item,[dict(phase,packing=packing)],set(phase['support']))
                    options = eq.StabilityOptions()
                    options.prepared_trials = eq.prepare_supplied_trials(spec.model,T,reclosed)
                    trial, = eq.stability_test(compiled,central,options).trials
                    evidence.update(reclosed_evidence=trial.evidence,reclosed_quantities=jsonable(trial.quantities))
                    if root['returned']=='liquid' and trial.evidence=='evaluated' and trial.quantities['tpd_over_rt']<0:
                        guesses.append([primary,(x,packing)])
            entry['supplied_pressure_roots'] = supplied
            if report.trials:
                native = [t for t in report.trials
                          if t.resolved_descent and t.quantities.get('density_side')==2 and t.split_coordinates]
                for trial in sorted(native,key=lambda t:t.quantities['split_delta_g_over_rt']):
                    z = list(trial.split_coordinates)
                    n = len(spec.parameters.component_ids)
                    if len(z)==n+2+len(trial.phase.support)+2:
                        phases = [(list(map(math.exp,z[:n])),math.exp(z[n+1])),
                                  (list(trial.composition),math.exp(z[-1]))]
                    else:
                        phases = [primary,(list(trial.composition),math.exp(z[-1]))]
                    guesses.insert(0,phases)
            entry['liquid_directed'] = bool(guesses)
            for guess in guesses if row['key'] not in ('weiland-1998:31:problem','lawson-1976-viii:0:problem') else []:
                attempt = coexistence(spec,parent,parent_g,guess,inspect=inspect)
                entry['attempts'].append(attempt)
                if attempt['confirmed']:
                    solutions[entry['key']] = last[0]
                    break
            if guesses and not any(a['confirmed'] for a in entry['attempts']):
                unresolved.append((entry,parent,parent_g))
        except (AssertionError, ValueError, RuntimeError) as error:
            entry['classification_error'] = str(error)
    for entry,parent,parent_g in sorted(unresolved,key=lambda item: item[0]['key'] in (
            'weiland-1998:31:problem','lawson-1976-viii:0:problem')):
        if entry['key']=='weiland-1998:31:problem':
            target = entry['feed_mol']
            carbon = spec.parameters.component_ids.index('carbon-dioxide')
            other, seed = min(
                ((r,a) for r in results if r.get('temperature_K')==entry['temperature_K']
                 and r['feed_mol'][:carbon]+r['feed_mol'][carbon+1:]==target[:carbon]+target[carbon+1:]
                 for a in r['attempts'] if a['confirmed']),
                key=lambda pair: abs(pair[0]['feed_mol'][carbon]-target[carbon]))
            start = solutions[other['key']]
            amine = target[spec.parameters.component_ids.index(route.config['amine'])]
            difference = target[carbon]-other['feed_mol'][carbon]
            steps = round(abs(difference)/amine/.0025)
            assert steps>0 and math.isclose(abs(difference),steps*.0025*amine,abs_tol=math.ulp(target[carbon]))
            guess = list(zip(seed['phases'],seed['packings'],strict=True))
            trace = entry['continuation'] = []
            for i in range(1,steps+1):
                feed = target.copy()
                if i!=steps:
                    feed[carbon] = other['feed_mol'][carbon]+math.copysign(i*.0025*amine,difference)
                declared = parent.feed
                declared.values = feed
                parent.feed = declared
                center = eq.solve_equilibrium(spec.model,parent)
                if not center.requested_tolerance_met:
                    trace.append(dict(feed_mol=feed,message=center.message))
                    break
                g = gibbs(eq.compile_problem(spec.model,parent),center)
                attempt = coexistence(spec,parent,g,guess,inspect=inspect,start=start)
                attempt.update(feed_mol=feed,seed_from=other['key'])
                trace.append(attempt)
                if not attempt['requested_tolerance_met'] or min(attempt['amounts_mol'],default=0)<=0:
                    break
                start = last[0]
            if trace[-1]['feed_mol']==target and 'confirmed' in trace[-1]:
                entry['attempts'].append(trace[-1])
            continue
        neighbors = sorted(
            ((r,a) for r in results for a in r['attempts'] if a['confirmed']),
            key=lambda pair: (abs(entry['temperature_K']-pair[0]['temperature_K']),
                              abs(math.log(entry['pressure_Pa']/pair[0]['pressure_Pa']))),
        )[:3]
        if entry['key']=='lawson-1976-viii:0:problem':
            neighbors.sort(key=lambda pair: pair[0]['key']!='weiland-1998:32:problem')
        for other,seed in neighbors:
            attempt = coexistence(spec,parent,parent_g,list(zip(seed['phases'],seed['packings'],strict=True)),inspect=inspect)
            entry['attempts'].append(dict(attempt, seed_from=other['key']))
            if attempt['confirmed']:
                solutions[entry['key']] = last[0]
                break
    return results


def write_classification(route, point, search_record, output):
    rows = route.result(search_record)
    started = time.monotonic()
    result = classify(route, point, rows, route.states(route.bind(point)))
    counts = dict(descents=len(result), liquid_directed=sum(e.get('liquid_directed', False) for e in result),
                  confirmed=sum(any(p['confirmed'] for p in e['attempts']) for e in result),
                  classification_errors=sum('classification_error' in e for e in result))
    route.write(output, dict(counts=counts, states=result, seconds=time.monotonic()-started))
    print(route.out.name, output, counts, flush=True)


def main(case):
    from refit_404 import DECLARATIONS, RUN, Route, stable

    assert case in ('main', 'sensitivity', 'penalty-0', 'penalty-1')
    suffix = '-sensitivity' if case=='sensitivity' else ''
    route = Route(DECLARATIONS/f'AMP-05e94210{suffix}.json',RUN/case)
    route.check_run_output()
    if case.startswith('penalty-'):
        for i, stage in enumerate(route.result('finding.json').get('stages', [])):
            if 'full_search' in stage:
                point = stable.read(sorted((route.out/f'penalized-{i}').glob('stage-*/parameters.json'))[-1])
                write_classification(route, point, stage['full_search']['search_record'], f'phase-penalized-{i}.json')
        return
    for entry in route.result('fits.json'):
        index = entry['start']
        write_classification(route, entry['endpoint'], f'search-{index}.json', f'phase-classification-{index}.json')


if __name__=='__main__':
    import sys
    main(sys.argv[1])
