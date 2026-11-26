"""Fixed-pressure AMP and MDEA comparisons and the worked AMP certificate."""
# ruff: noqa: E402
import math
import sys
from time import monotonic

from round_3.recall import DECLARATION, ENDPOINTS
from part_ii import ROOT, Route, calculation_declaration, deviation_statistics, eq, jsonable, reg, stable
from reference_states_428 import amp, balances, identity, phase, phase_closure
from r4_shift_tables_426 import available_prediction, temperature_band
from amp_transfer import classify_descents as cd

sys.path.insert(0, str(ROOT / 'analyses/mdea_mea_workflow/scripts'))
from bounded_binary_411 import DECLARATION as MDEA, RESULTS as BOUNDED
from shared_bicarbonate_417 import dilute_vapor_connection

FULL = 'lowest-G feasible assemblage found among the tested supports'


def trials(report):
    return [dict(seed=t.seed, kind=t.phase.kind.name, support=list(t.phase.support), composition=list(t.composition),
                 evidence=t.evidence, message=t.message, descent=t.resolved_descent, quantities=t.quantities,
                 optimizer_success=t.optimizer.success, optimizer_tolerance_met=t.optimizer.requested_tolerance_met)
            for t in report.trials]


def physical(spec, problem, result, *, reclose=True, compiled=None, standard=None):
    ids = spec.parameters.component_ids
    formulas = [spec.spec['element_formulas'][c] for c in ids]
    T, P = result.temperature, result.pressure
    rows = [phase(spec.model, T, P, n, rho, result.phase_mole_fractions(i), formulas)
            for i, (n, rho) in enumerate(zip(result.amounts, result.molar_densities, strict=True))]
    phases = problem.phases
    candidates = [r for i,r in enumerate(rows)
                  if reclose and abs(r['pressure_residual_Pa'])/P>problem.row_tolerance
                  and (min(r['x'])>0 or (len(phases)==len(rows) and phases[i].kind.name=='Liquid'))]
    if candidates:
        from fixed_reaction_reference.reference_derivatives import pressure_reclosure

        if standard is None:
            if compiled is None:
                compiled = eq.compile_problem(spec.model, problem)
            standard = eq.stability_test(compiled, result).standard_over_rt
        for row in candidates:
            x, rho = row['x'], row['density_mol_m3']
            new_rho, state, evidence = pressure_reclosure(
                spec.model, problem, T, P, rho, x, standard, spec.model.state(T, rho=rho, x=x))
            row.update(original_pressure_residual_Pa=row['pressure_residual_Pa'],
                       original_density_mol_m3=rho, pressure_reclosure=evidence,
                       density_mol_m3=new_rho, pressure_Pa=state.pressure, pressure_residual_Pa=state.pressure-P)
    residuals = balances(problem.feed.values, rows, formulas)
    checks = dict(phases=rows,balances=residuals)
    return dict(checks,physical_checks_pass=phase_closure(checks,P,problem.row_tolerance),
                residuals=list(result.residuals),row_tolerance=problem.row_tolerance)


def fixed(route, spec, state, P, seed, *, mdea=False, assemblages=False, decision_bubble=False, checkpoint=None):
    item = route.stability_row(spec, state, 1.)
    problem, model = item.problem, spec.model
    problem.pressure = type(problem.pressure).fixed(P)
    item.pressure_reference = None
    result = eq.solve_equilibrium(model, problem)
    compiled = eq.compile_problem(model, problem)
    out = dict(T_K=result.temperature, P_Pa=P, realized_Pa=result.pressure, feed_mol=list(problem.feed.values),
               species=list(spec.parameters.component_ids), declaration=calculation_declaration(problem),
               status=result.message, attempts=[])
    parent_g, guess, native, seeds = None, None, [], []
    if result.requested_tolerance_met:
        x, rho = list(result.phase_mole_fractions(0)), result.molar_densities[0]
        guess = (x, result.packing_fractions[0])
        out.update(physical(spec, problem, result))
        if checkpoint is not None:
            checkpoint(out)
        out['roots'] = cd.pressure_roots(model, result.temperature, P, x, rho)
        prediction = reg.predict(model, item)
        out['search'] = cd.jsonable(stable.stability_payload(prediction))
        parent_g = cd.gibbs(compiled, result)
        out['parent_gibbs_RT_mol'] = parent_g
        if prediction.stability is not None:
            native = trials(prediction.stability.report)
            seeds = [t for t in prediction.stability.report.trials if t.resolved_descent and t.split_coordinates
                     and t.quantities.get('density_side')==2 and len(t.phase.support)==len(x)]
        if seed and seed.get('witness'):
            witness = seed['witness']
            supplied, absent, *_ = stable._applicable(item, [witness], set(range(len(x)))-set(compiled.removed_species))
            options = eq.StabilityOptions()
            options.prepared_trials = eq.prepare_supplied_trials(model, result.temperature, supplied)
            out['supplied'] = trials(eq.stability_test(compiled, result, options)) if supplied else absent
    out['native_trials'] = native
    resolved = any(t['descent'] for t in native) or any(
        stable.supplied_negative(t) for t in out.get('supplied', []) if 'quantities' in t)
    out['instability'] = 'resolved descent' if resolved else 'finite search, no resolved descent' if (
        out.get('search', {}).get('no_descent_in_trial_set')) else 'unresolved' if result.requested_tolerance_met else 'unavailable'
    pair_solution = []
    if seed and (resolved or mdea or not assemblages):
        attempts = [list(zip(seed['pair']['phases'], seed['pair']['packings'], strict=True))]
        if guess is not None and not mdea:
            for t in sorted(seeds,key=lambda t:t.quantities['split_delta_g_over_rt']):
                z, n = t.split_coordinates, len(guess[0])
                donor = (list(map(math.exp,z[:n])),math.exp(z[n+1])) if len(z)==2*n+4 else guess
                attempts.append([donor,(list(t.composition),math.exp(z[-1]))])
        def inspect(compiled, solved):
            pair_solution[:] = compiled, solved
            if solved.requested_tolerance_met and len(solved.amounts)==2 and min(solved.amounts)>0:
                details = physical(spec, problem, solved, compiled=compiled)
                return {k:details[k] for k in ('balances', 'physical_checks_pass')}

        for index, guesses in enumerate(attempts):
            try:
                pair = cd.coexistence(spec, problem, parent_g, guesses, inspect=inspect)
                pair.update(pair.pop('diagnostics') or {}, seed='archive' if index==0 else 'native split')
                out['attempts'].append(pair)
                if 'phases' in pair:
                    if mdea:
                        pair['dilute_vapor_traces'] = [dilute_vapor_connection(model, result.temperature, x, rho)
                                                       for x, rho in zip(pair['phases'], pair['densities_mol_m3'], strict=True)]
                if pair['confirmed']:
                    break
            except (ValueError, RuntimeError) as error:
                out['attempts'].append(dict(confirmed=False, message=str(error)))
    distances = [t for t in native+out.get('supplied', []) if (t.get('descent') or t.get('evidence') in ('evaluated','no_resolved_descent')) and 'quantities' in t
                 and 'tpd_over_rt' in t['quantities']]
    out['minimum_trial'] = min(distances, key=lambda t: t['quantities']['tpd_over_rt'], default=None)
    if (best := out['minimum_trial']) is not None:
        out['minimum_trial_roots'] = cd.pressure_roots(model, result.temperature, P, best['composition'],
                                                       1/best['quantities']['volume_m3_per_mol'])
    if resolved:
        out['liquid_vapor'] = liquid_vapor(spec, route, problem, guess, parent_g)
        if decision_bubble:
            pair = out['liquid_vapor']
            out['bubble_inputs'] = dict(T_K=out['T_K'],feed_mol=out['feed_mol'],pressure_guess_Pa=P,
                                       parent_seed=guess,pair_packings=pair.get('packings'),
                                       pair_compositions=[p['x'] for p in pair.get('phases',[])])
            if checkpoint is not None:
                checkpoint(out)
            try:
                out['bubble'] = liquid_vapor(spec, route, problem, guess, parent_g, incipient=True, seed=pair)
                if not out['bubble']['qualified']:
                    out['bubble_refusal'] = out['bubble']['message']
            except (ValueError,RuntimeError,AttributeError) as error:
                out['bubble_refusal'] = f'{type(error).__name__}: {error}'
            if checkpoint is not None:
                checkpoint(out)
        if assemblages:
            amp_candidates(spec, route, problem, out, pair_solution)
    return out


def liquid_vapor(spec, route, parent, guess, parent_g, *, incipient=False, seed=None):
    problem = parent
    original = parent.phases
    pressure = type(parent.pressure).fixed(parent.pressure.value)
    liquid = type(original[0])()
    liquid.name, liquid.kind, liquid.support_declared = 'L', original[0].kind, True
    liquid.support = original[0].support
    x, packing = guess
    liquid.composition_guess, liquid.packing_guess = [x[j] for j in liquid.support], packing
    vapor = type(liquid)()
    vapor.name, vapor.kind, vapor.support_declared = 'V', type(liquid.kind).Vapor, True
    vapor.support = [spec.parameters.component_ids.index(c) for c in route.config['vapor_species']]
    if incipient:
        vapor.amount = type(vapor.amount).pinned(0.)
        problem.pressure = type(problem.pressure).variable(problem.pressure.value)
        if seed and seed.get('phases'):
            liquid.composition_guess = [seed['phases'][0]['x'][j] for j in liquid.support]
            vapor.composition_guess = [seed['phases'][1]['x'][j] for j in vapor.support]
            liquid.packing_guess, vapor.packing_guess = seed['packings']
    problem.phases = [liquid, vapor]
    try:
        result = eq.solve_equilibrium(spec.model, problem)
        compiled = eq.compile_problem(spec.model, problem)
    finally:
        problem.phases, problem.pressure = original, pressure
    out = dict(support='L+incipient V' if incipient else 'L+V', message=result.message, qualified=False,
               T_K=result.temperature, pressure_Pa=result.pressure, amounts_mol=list(result.amounts),
               feed_mol=list(problem.feed.values), row_tolerance=problem.row_tolerance,
               requested_tolerance_met=result.requested_tolerance_met)
    if result.requested_tolerance_met and len(result.amounts)==2:
        out.update(physical(spec, problem, result, compiled=compiled), packings=list(result.packing_fractions))
        x, rho = [row['x'] for row in out['phases']], list(result.molar_densities)
        trace, connected = dilute_vapor_connection(spec.model, result.temperature, x[1], rho[1])
        out.update(vapor_trace=trace, vapor_connected=connected)
        distinct = (max(abs(a-b) for a,b in zip(*x,strict=True))>cd.COINCIDENCE or
                    abs(math.log(rho[0]/rho[1]))>cd.COINCIDENCE)
        out['qualified'] = out['physical_checks_pass'] and connected and distinct and result.amounts[0]>0
        if incipient:
            out['qualified'] &= result.amounts[1]==0
        else:
            g, err = cd.gibbs(compiled,result)
            out.update(Gibbs_over_RT_mol=g, error=err)
            out.update(Gibbs_decrease_over_RT_mol=parent_g[0]-g, numerical_error_over_RT_mol=parent_g[1]+err)
            out['qualified'] &= (result.amounts[1]>0 and
                                 out['Gibbs_decrease_over_RT_mol']>out['numerical_error_over_RT_mol'])
    return out


def amp_candidates(spec, route, problem, out, pair_solution):
    model = spec.model
    vapor = [spec.parameters.component_ids.index(c) for c in route.config['vapor_species']]
    support = [i for i in range(len(spec.parameters.component_ids))
               if i not in eq.compile_problem(model, problem).removed_species]
    pair = next((a for a in out['attempts'] if a['confirmed']), None)
    g, error = out['parent_gibbs_RT_mol']
    candidates = [dict(support='L', Gibbs_over_RT_mol=g, error=error, qualified=out['physical_checks_pass']),
                  out['liquid_vapor']]
    out['candidates'] = candidates
    original = problem.phases
    pressure = type(problem.pressure).fixed(problem.pressure.value)

    def make_phase(name, kind, support, guess=(None, None), pinned=False):
        phase = type(original[0])()
        phase.name, phase.kind = name, getattr(type(original[0].kind), kind)
        phase.support, phase.support_declared = support, True
        x, phase.packing_guess = guess
        if x is not None:
            phase.composition_guess = [x[i] for i in support]
        if pinned:
            phase.amount = type(phase.amount).pinned(0.)
        return phase

    variants = []
    if pair:
        compiled, solved = pair_solution
        omitted = trials(eq.stability_test(compiled, solved))
        candidates.append(dict(support='L1+L2', qualified=True, pressure_Pa=solved.pressure,
                               Gibbs_over_RT_mol=pair['split_Gibbs_over_RT_mol'],
                               error=pair['numerical_error_over_RT_mol']-error,
                               amounts_mol=pair['amounts_mol'], omitted_phase_trials=omitted))
        liquid = [make_phase(f'L{i+1}', 'Liquid', support, seed)
                  for i, seed in enumerate(zip(pair['phases'], pair['packings'], strict=True))]
        seed = next(t for t in out['native_trials'] if t['kind']=='Vapor' and t['seed']=='positive-neutral-base')
        vapor_guess = (seed['composition'], None)
        variants.append(('L1+L2+incipient V', liquid+[make_phase('V', 'Vapor', vapor, vapor_guess, pinned=True)]))
        if any(t['kind']=='Vapor' and t['descent'] for t in omitted):
            variants.append(('L1+L2+V', liquid+[make_phase('V', 'Vapor', vapor, vapor_guess)]))
    else:
        candidates.append(dict(support='L1+L2', qualified=False, message='Seeded attempts did not confirm distinct liquid roots below parent Gibbs beyond paired error.'))
    for kind, phases in variants:
        entry = dict(support=kind, qualified=False)
        candidates.append(entry)
        incipient = 'incipient' in kind
        try:
            problem.phases = phases
            problem.pressure = type(pressure).variable(pressure.value) if incipient else pressure
            solved = eq.solve_equilibrium(model, problem)
            entry.update(message=solved.message, pressure_Pa=solved.pressure, amounts_mol=list(solved.amounts),
                         requested_tolerance_met=solved.requested_tolerance_met)
            if solved.requested_tolerance_met and solved.amounts:
                entry.update(physical(spec, problem, solved))
                roots = [cd.pressure_roots(model, solved.temperature, solved.pressure, p['x'], p['density_mol_m3'])
                         for p in entry['phases']]
                entry['roots'] = roots
                wanted = ['liquid']*(len(phases)-1)+['vapor']
                entry['root_checks_pass'] = all(any(r['returned']==branch for r in cd.matched(test, problem.row_tolerance))
                                                for branch, test in zip(wanted, roots, strict=True))
                entry['qualified'] = (entry['physical_checks_pass'] and entry['root_checks_pass']
                                      and min(solved.amounts[:(-1 if incipient else None)])>0)
                if not incipient:
                    compiled = eq.compile_problem(model, problem)
                    entry['Gibbs_over_RT_mol'], entry['error'] = cd.gibbs(compiled, solved)
                    entry['omitted_phase_trials'] = trials(eq.stability_test(compiled, solved))
        except (ValueError, RuntimeError) as error:
            entry.update(message=str(error))
        finally:
            problem.phases, problem.pressure = original, pressure
    eligible = sorted((c for c in candidates if c['qualified'] and 'Gibbs_over_RT_mol' in c), key=lambda c: c['Gibbs_over_RT_mol'])
    out['lowest_found'] = dict(scope=FULL, support=eligible[0]['support']) if eligible else None
    out['unresolved_supports'] = [c['support'] for c in candidates if not c['qualified'] and 'incipient' not in c['support']]
    if len(eligible)>1 and eligible[1]['Gibbs_over_RT_mol']-eligible[0]['Gibbs_over_RT_mol'] <= eligible[0]['error']+eligible[1]['error']:
        out['lowest_found']['comparison'] = 'Gibbs difference within paired numerical error'
    out['stable_assemblage'] = None


def amp_rows(work, save, *, save_q1=True):
    start = monotonic()
    route = Route(DECLARATION, work)
    paths = [ENDPOINTS / name / 'parameters.json' for name in ('main', 'slope-150')]
    specs = [route.bind(stable.read(p)) for p in paths]
    states = {r['key']: r for r in route.states(specs[0])}
    main = ENDPOINTS / 'main'
    search, class_file, measured, data_file = [main / f for f in ('search-1.json.gz', 'phase-classification-1.json.gz', 'measured-states.json', 'data-rows.json')]
    archive = {r['key']: r for r in stable.read(search)}
    seeds = {}
    for row in stable.read(class_file)['states']:
        pair = next((a for a in row['attempts'] if a['confirmed']), None)
        if pair:
            witness = next((r for r in row['supplied_pressure_roots'] if stable.supplied_negative(r['witness'])), None)
            seeds[row['key']] = dict(row, pair=pair, witness=None if witness is None else dict(
                witness['witness']['phase'], packing=witness.get('reclosed_quantities', witness['witness']['quantities'])['packing_fraction']))
    worked = next(k for k in seeds if '393.15:0.7:1.05' in k and '11.545384436618988' in k)
    onset = [k for k in archive if '11.545384436618988' in k and k.endswith(('393.15:0.3:1.05','393.15:0.4:1.05'))]
    confirmed = [r['key'] for r in stable.read(measured)['start-1'] if r['confirmed']]
    records = [{r['identity']: r for r in spec.inputs['observations']['comparisons']} for spec in specs]
    keys = [r['identity'] for r in stable.read(data_file) if r['identity'].startswith(('hartono-2021:', 'tong-2012:'))
            and r['role']=='not fitted' and r['basis']=='Total equilibrium pressure' and temperature_band(r['T_K'])=='stripper']
    assert len(confirmed)==6 and len(onset)==2 and len(keys)==43
    datasets = specs[0].spec['datasets']
    sources = {specs[0].path.parent/d['path'] for d in datasets if d.get('path')}
    inputs = identity(*paths, DECLARATION, specs[0].path, search, class_file, measured, data_file,
                      ENDPOINTS/'slope-150/data-rows.json', *sorted(sources))
    for endpoint, prefix in zip(paths, ('d69f7e9d','5c0bf32b'), strict=True):
        assert inputs[str(endpoint.relative_to(ROOT))].startswith(prefix)
    rows, observed = [], {}
    for key, label, P in [*((k, 'archived search pressure', archive[k]['supplied_parent_pressure_Pa']) for k in [worked,*onset,*confirmed]),
                          *((k, 'measured pressure', 1000*float(records[0][k.removesuffix(':problem')]['row']['P_total_kPa'])) for k in confirmed)]:
        seed = seeds.get(key)
        if seed is None:
            neighbor = min(seeds.values(), key=lambda r: (abs(r['temperature_K']-route.temperature(specs[0], states[key])),
                                                           abs(math.log(r['pressure_Pa']/P))))
            seed = dict(neighbor, witness=None)
        free, fixed_fit = [fixed(route, spec, states[key], P, seed, assemblages=(label=='measured pressure' and i==0))
                           for i, spec in enumerate(specs)]
        assert free['feed_mol']==fixed_fit['feed_mol'] and free['T_K']==fixed_fit['T_K']
        rows.append(dict(key=key, pressure_basis=label, free=free, fixed=fixed_fit))
        if label=='measured pressure':
            observed[key] = free
    if save_q1:
        save('q1', start, rows=rows, inputs=inputs)
    start = monotonic()
    rows = []
    for index, key in enumerate(keys):
        definitions = [r[key] for r in records]
        assert all(definitions[0][field]==definitions[1][field] for field in ('identity','row','unit','problem','basis'))
        predictions = [spec.prediction(r) for spec, r in zip(specs, definitions, strict=True)]
        P, state = predictions[0]['observed'], dict(problem=definitions[0]['problem'])
        assert P==predictions[1]['observed']
        T = route.temperature(specs[0], state)
        nearest = min(seeds.values(), key=lambda r: (abs(r['temperature_K']-T), abs(math.log(r['pressure_Pa']/P))))
        assessment = observed.get(state['problem'])
        projected = (monotonic()-start)/max(1,index)*len(keys)
        if assessment is None:
            assessment = (dict(instability='unavailable', status='Fixed-P follow-up exceeded projected 600 s budget') if projected>=600 else
                          fixed(route, specs[0], state, P, seeds.get(state['problem'], nearest), assemblages=True))
        rows.append(dict(identity=key, observed_Pa=P, T_K=T, source=definitions[0]['row'], predictions=predictions, measured_pressure_search=assessment))
    scores = {}
    for source in ('hartono-2021', 'tong-2012'):
        group = [r for r in rows if r['identity'].startswith(source+':')]
        matched = [r for r in group if all(map(available_prediction, r['predictions']))]
        scores[source] = dict(total=len(group), matched=len(matched), excluded=[r['identity'] for r in group if r not in matched],
                              baseline=sum(float(r['source']['alpha_mol_CO2_per_mol_AMP'])==0 for r in group),
                              fixed_pressure_outcomes={o:sum(r['measured_pressure_search']['instability']==o for r in group)
                                                       for o in sorted({r['measured_pressure_search']['instability'] for r in group})},
                              **{name:deviation_statistics([(r['observed_Pa'],r['predictions'][i]['value']) for r in matched], 'Pa')
                                 for i,name in enumerate(('free','fixed'))})
    save('q2', start, rows=rows, scores=scores, inputs=inputs)
    assert round(scores['tong-2012']['fixed']['AARD_percent'],2)==25.47


def mdea_rows(work, save):
    start = monotonic()
    parent = BOUNDED.parent/'shared-bicarbonate-417/mdea'
    low, high = [next(parent.glob(f'mdea-{label}-*/endpoint.json.gz')) for label in ('low','high')]
    archive = low.with_name('stability.json.gz')
    ref = [r for r in stable.read(archive)['pressure_roots'] if r['phase_identity']=='two liquids']
    assert len(ref)==2
    rows = []
    route = Route(MDEA, work)
    for k, path in zip((.1325000116847309, .7650000233694618, 1.), (low, BOUNDED/'endpoint.json', high), strict=True):
        point = stable.read(path)
        pair = next(c for b in point['parameters']['pairs'] if {b['component_id_a'], b['component_id_b']}=={'water','bicarbonate-anion'}
                    for c in b['coefficients'] if c['family']=='k_ij')
        assert pair['value']['magnitude']==k
        spec = route.bind(point)
        for old in ref:
            pair = next(a for a in old['attempts'] if a['confirmed'])
            T, P = old['temperature_K'], old['pressure_Pa']
            stock = {c: n for c, n in zip(spec.parameters.component_ids, old['feed_mol'], strict=True)
                     if n>0 and c!='carbon-dioxide'}
            state = dict(stock=stock,T=T,a=old['feed_mol'][list(spec.parameters.component_ids).index('carbon-dioxide')])
            row = fixed(route, spec, state, P, dict(pair=pair), mdea=True)
            attempt = row['attempts'][0]
            tolerance = pair['numerical_error_over_RT_mol']
            observed = attempt.get('Gibbs_decrease_over_RT_mol')
            rows.append(dict(row, key=old['key'], k=k, reference=pair['Gibbs_decrease_over_RT_mol'],
                             reference_error=tolerance, within_reference_error=observed is not None and abs(observed-pair['Gibbs_decrease_over_RT_mol'])<=tolerance))
    inputs = identity(low,high,archive,BOUNDED/'endpoint.json',MDEA,spec.path,
                      MDEA.parent/route.config['dataset_changes']['path'])
    assert all(inputs[str(p.relative_to(ROOT))].startswith(prefix) for p,prefix in
               [(low,'e2facb93'),(high,'d43c72a3'),(BOUNDED/'endpoint.json','98488f92')])
    save('q3', start, rows=rows, inputs=inputs)
    assert all(r['within_reference_error'] and r['attempts'][0]['confirmed'] for r in rows[:2])


def worked(work, save, inspect):
    start = monotonic()
    record = amp(work, inspect=inspect)
    save('q6', start, **record)
    assert all(record['checks'].values())


def certificate(spec, problem, compiled, result):
    from reference_states_428 import source_log_k

    if not result.requested_tolerance_met or not result.amounts:
        return dict(status='pair unavailable', message=result.message)
    ids = spec.parameters.component_ids
    tolerance = problem.row_tolerance
    a = eq.reaction_activities(spec.model, result)
    chemical = [dict(phase=r.phase, species=ids[r.index], residual=value, tolerance=tolerance)
                for r, value in zip(result.rows, result.residuals, strict=True) if r.kind.name=='Chemical']
    gauge = dict(zip(compiled.coordinate_labels(), result.coordinates, strict=True))['phi[charge row 0]']
    charges = [spec.spec['element_formulas'][c]['charge'] for c in ids]
    phase_logs = [next(row.species.log_activities for row in a if row.phase_index==p and row.reaction_index==1)
                  for p in range(2)]
    transfer = {c: l2-l1-z*gauge for c, l1, l2, z in zip(ids, *phase_logs, charges, strict=True)}
    reactions = []
    for row in a:
        reaction = problem.reactions[row.reaction_index]
        Q = math.fsum(n*log for n, log in zip(reaction.stoichiometry, row.species.log_activities, strict=True) if n)
        K = source_log_k(reaction.correlation, result.temperature)
        reactions.append(dict(phase=row.phase_index, reaction=reaction.name, ln_Q=Q, ln_K=K, residual=Q-K,
                              tolerance=tolerance*sum(map(abs,reaction.stoichiometry)), basis=row.basis))
    vapor = type(problem.phases[0])()
    vapor.name, vapor.kind = 'neutral vapor test', type(problem.phases[0].kind).Vapor
    vapor.support = [i for i, z in enumerate(charges) if not z]
    vapor.support_declared = True
    options = eq.StabilityOptions()
    options.trials = [vapor]
    report = eq.stability_test(compiled, result, options)
    evaluated = trials(report)
    endpoints = [t for t in evaluated if (t['descent'] or t['evidence'] in ('evaluated','no_resolved_descent'))
                 and 'tpd_over_rt' in t['quantities']]
    for t in endpoints:
        rho = 1/t['quantities']['volume_m3_per_mol']
        trace, connected = dilute_vapor_connection(spec.model, result.temperature, t['composition'], rho)
        roots = cd.pressure_roots(spec.model, result.temperature, result.pressure, t['composition'], rho)
        liquid = any(r['returned']=='liquid' for r in cd.matched(roots, tolerance))
        t.update(density_mol_m3=rho, dilute_vapor_trace=trace, vapor_connected=connected, roots=roots,
                 endpoint='dilute-vapor-connected' if connected else 'liquid' if liquid else 'unresolved')
    tpd = [t['quantities']['tpd_over_rt'] for t in endpoints]
    return dict(gauge_phi_over_RT=gauge, primitive_chemical_rows=chemical, primitive_limit=tolerance,
                reaction_contractions=reactions, electrochemical_difference_L2_minus_L1=transfer, transfer_limit=2*tolerance,
                trial_minimum=min(tpd, default=None), vapor_trials=evaluated, vapor_message=report.message,
                vapor_connected_minimum=min((v for t,v in zip(endpoints,tpd,strict=True) if t['vapor_connected']), default=None),
                vapor_completed=report.completed, vapor_no_descent=report.no_descent_in_trial_set,
                reaction_pass=all(abs(row['residual'])<=row['tolerance'] for row in reactions),
                transfer_pass=max(map(abs,transfer.values()))<=2*tolerance,
                primitive_pass=max(map(abs,result.residuals))<=tolerance)
