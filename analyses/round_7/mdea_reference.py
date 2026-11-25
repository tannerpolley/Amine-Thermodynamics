"""Pressure-reference and measured-parent readbacks for MDEA."""
# ruff: noqa: E402
from collections import Counter, defaultdict
import math
import sys
from time import monotonic

from calculations import MDEA, OUT, SALT, WORK, a, mdea_incumbent, r, save, transfer

from classify_descents import COINCIDENCE, DENSITY_WINDOW, matched
from comparisons import mdea_deviations
from part_ii import Route, epcsaft, eq, np
from phases import fixed
from reaction_reference import FixedReference, reference_readback
from verify_reference_calorics import first_actions, observable

R = epcsaft.GAS_CONSTANT_J_PER_MOL_K
PHASE421 = MDEA.RESULTS.parent / 'phase-search-421'
SOBRINO = {6: (.1000, 948.6), 12: (.2002, 954.), 18: (.3000, 959.6), 24: (.4000, 964.2)}


def route(case, name, cls=Route):
    shared = (transfer.SHARED, r.s.sha256(transfer.SHARED)) if case=='salt' else None
    return cls(MDEA.DECLARATION, WORK / name / case / cls.__name__, shared_values=shared)


def seed_state(spec, entry):
    feed = dict(zip(spec.parameters.component_ids, entry['feed_mol'], strict=True))
    loading = feed.pop('carbon-dioxide') / feed['methyldiethanolamine']
    return dict(T=entry['temperature_K'], stock={c:n for c,n in feed.items() if n}, a=loading)


def predicates(outcome, *, tolerance):
    readback = outcome.get('reference_readback',{}).get('pair_readback',[])
    for i,result in enumerate(outcome['attempts']):
        checks = dict(requested_tolerance=result.get('requested_tolerance_met',False),
                      positive_amounts=len(result.get('amounts_mol',[]))==2 and min(result['amounts_mol'])>0,
                      balances_and_phases=result.get('physical_checks_pass',False),
                      distinct=result.get('distinct',False),
                      liquid_root=bool(result.get('roots')) and all(
                          any(x['returned']=='liquid' for x in matched(group,tolerance)) for group in result['roots']),
                      lowering=result.get('Gibbs_decrease_over_RT_mol',-math.inf)>result.get('numerical_error_over_RT_mol',math.inf))
        if i < len(readback) and readback[i]:
            checks['reaction'] = readback[i]['affinity_within_tolerance']
            checks['interphase'] = readback[i]['charge_neutral_transfer_within_tolerance']
        if checks['positive_amounts']:
            result['phase_fractions'] = [v/sum(result['amounts_mol']) for v in result['amounts_mol']]
        if result.get('phases'):
            result['separation'] = dict(max_delta_x=max(abs(i-j) for i,j in zip(*result['phases'],strict=True)),
                     log_density_ratio=abs(math.log(result['densities_mol_m3'][0]/result['densities_mol_m3'][1])))
        result['acceptance'] = checks
        result['disposition'] = ('confirmed' if all(checks.values()) else 'failed' if not checks['requested_tolerance']
            else 'coalesced' if checks['positive_amounts'] and not checks['distinct'] else 'unresolved')
    outcome['tolerances'] = dict(equilibrium_row=tolerance, coincidence=COINCIDENCE, log_root_matching=DENSITY_WINDOW)
    return outcome


def standard_derivatives(model, problem, solution):
    T,P = solution.temperature,solution.pressure
    x = np.array(solution.phase_mole_fractions(0))
    N,rho = solution.amounts[0],solution.molar_densities[0]
    eos_state = model.state(T,rho=rho,x=x)
    refs = problem.reactions
    mobile = [rx.name for rx in refs if rx.reference.reference_pressure_pa is None]
    caloric = {}

    def enthalpy(result):
        values = first_actions(model,problem,result,[observable('SystemEnthalpy',0)],[(0.,0.,[0.]*len(x))])
        return values[0][0][0]

    try:
        energy = enthalpy(solution)
        caloric['engine_system_enthalpy_J'] = energy
        reactions = problem.reactions
        for rx in reactions:
            if rx.name in mobile:
                rx.reference = eq.ReactionReference(rx.reference.source_basis,reference_pressure_pa=P)
        problem.reactions = reactions
        center = eq.solve_equilibrium(model,problem)
        if not center.requested_tolerance_met:
            raise ValueError(center.message)
        caloric.update(engine_frozen_at_same_pressure_J=enthalpy(center),
                       frozen_center_max_x_difference=max(abs(a-b) for a,b in zip(x,center.phase_mole_fractions(0),strict=True)))
        caloric['engine_tracking_minus_frozen_J'] = energy-caloric['engine_frozen_at_same_pressure_J']
    except (RuntimeError,ValueError) as exc:
        caloric['engine_enthalpy_refusal'] = str(exc)
    finally:
        problem.reactions = refs
    rows = []

    def offsets(t, p, source_p):
        decl = problem
        decl.temperature = type(decl.temperature).fixed(t)
        decl.pressure = type(decl.pressure).fixed(p)
        reactions = decl.reactions
        for rx in reactions:
            if rx.name in mobile:
                rx.reference = eq.ReactionReference(rx.reference.source_basis, reference_pressure_pa=source_p)
        decl.reactions = reactions
        res = eq.solve_equilibrium(model,decl)
        if not res.requested_tolerance_met:
            raise ValueError(res.message)
        return np.asarray(eq.stability_test(eq.compile_problem(model,decl),res).standard_over_rt)

    def total_g(t,p,source_p):
        state = model.state(t,P=p,x=x,phase='liquid')
        return R*t*N*float(x @ (np.log(x*state.molar_density) + state.residual_chemical_potential_over_rt
                                + offsets(t,p,source_p)))

    for dp,dt in ((P*1e-4,.04),(P*5e-5,.02),(P*2.5e-5,.01)):
        row = dict(step_Pa=dp,step_K=dt,eos_volume_m3=N/rho,moving_reactions=mobile,
                   eos_residual_enthalpy_J=N*eos_state.residual_enthalpy,**caloric)
        rows.append(row)
        try:
            derivative = (offsets(T,P,P+dp)-offsets(T,P,P-dp))/(2*dp)
            dT_Psrc = (offsets(T+dt,P,P)-offsets(T-dt,P,P))/(2*dt)
            pplus,pminus = [model.state(t,rho=rho,x=x).pressure for t in (T+dt,T-dt)]
            dP_dT = (pplus-pminus)/(2*dt)
            frozen_term = float(-R*T*T*N*(x @ dT_Psrc))
            moving_term = float(-R*T*T*N*(x @ (
                offsets(T+dt,P,pplus)-offsets(T-dt,P,pminus)))/(2*dt))
            row.update(offsets_over_rt=offsets(T,P,P), d_offsets_over_rt_dPsrc_Pa_inverse=derivative,
                       correction_m3=float(R*T*N*(x @ derivative)), dP_dT_Pa_K=dP_dT,
                       frozen_reference_term_J=frozen_term,moving_reference_term_direct_J=moving_term,
                       pressure_tracking_term_J=float(-R*T*T*N*(x @ derivative)*dP_dT),
                       pressure_tracking_direct_J=moving_term-frozen_term,
                       frozen_G_volume_m3=(total_g(T,P+dp,P)-total_g(T,P-dp,P))/(2*dp),
                       moving_G_volume_m3=(total_g(T,P+dp,P+dp)-total_g(T,P-dp,P-dp))/(2*dp))
        except (RuntimeError,ValueError) as exc:
            row['refusal'] = str(exc)
    return rows


def root_scan(model,T,P,compositions):
    out = []
    for x in compositions:
        row = dict(x=x)
        out.append(row)
        try:
            roots = model.density_diagnostics(T,P,x=x)
            def reduced(points):
                return [{k:getattr(q,k) for k in ('molar_density','pressure','pressure_density_derivative',
                         'mechanical_sign','lower','upper','residual','cause','stop')} for q in points]
            row.update(roots=reduced(roots.pressure_roots),unresolved=reduced(roots.unresolved),
                       density_settings=roots.solver_options,stop=roots.stop,evaluations=roots.evaluations)
        except (RuntimeError,ValueError) as exc:
            row['refusal'] = str(exc)
    return out


def reference():
    start = monotonic()
    source = SALT/'search-outcome.json.gz'
    archived = r.read(source)
    key, = archived['confirmed']
    entry = next(row for row in archived['classifications'] if row['key']==key)
    assert (entry['temperature_K'],entry['pressure_Pa']) == (383.15,121308970.11859363)
    point, path = mdea_incumbent('salt')
    comparisons = {}
    for cls, label in ((Route,'tracking'),(FixedReference,'100 kPa')):
        run = route('salt','A',cls)
        spec = run.bind(point)
        state = seed_state(spec,entry)
        item = run.stability_row(spec,state,1.)
        parent = item.problem
        T,P = state['T'],entry['pressure_Pa']
        parent.pressure = type(parent.pressure).fixed(P)
        solution = eq.solve_equilibrium(spec.model,parent)
        baseline = fixed(run,spec,state,P,dict(pair=entry['attempts'][0]),mdea=True)
        try:
            baseline['reference_readback'] = reference_readback(run,spec,state,T,P,baseline)
        except (RuntimeError,ValueError) as exc:
            baseline['reference_readback'] = dict(refusal=str(exc))
        if solution.requested_tolerance_met:
            baseline['fixed_inventory_derivatives'] = standard_derivatives(spec.model,parent,solution)
        else:
            baseline['fixed_inventory_refusal'] = solution.message
        for result in baseline['attempts']:
            if result.get('phases'):
                result['root_scan'] = root_scan(spec.model,T,P,result['phases'])
        comparisons[label] = predicates(baseline,tolerance=parent.row_tolerance)
    low = a.ANALYSES/'round_3/results/q4.json'
    save(OUT/'A/reference.json.gz',dict(seconds=monotonic()-start, projected_control_s=33,
         low_pressure_controls=r.read(low)['checks'], low_pressure_sha256=r.s.sha256(low),
         archive=entry, wheel_sha256=r.SHA, parameter_sha256=r.s.sha256(path), source_sha256=r.s.sha256(source),
         comparisons=comparisons))


def census():
    start = monotonic()
    history = r.read(PHASE421/'coverage-counts.json')
    coverage = {x['key']: x for x in r.read(PHASE421/'coverage.json') if x['tier']=='data'}
    rows = {x['key']: x for x in r.read(SALT/'search-0.json.gz') if x['key'] in coverage}
    salt_data = {x['identity']:x for x in r.read(SALT/'data-rows.json.gz')}
    classifications = {x['key']:x for x in r.read(SALT/'search-outcome.json.gz')['classifications']}
    point, source = mdea_incumbent('salt')
    run = route('salt', 'B')
    spec = run.bind(point)
    fit = {x['identity']:x for x in spec.inputs['observations']['fitted']}
    assert coverage.keys()==rows.keys() and len(rows)==1564
    below = {k for k,v in history['canonical'].items() if v['ratio'] < 1}
    below_observations = {coverage[k]['observation'] for k in below}
    assert len(below)==27 and len(below_observations)==25
    salt_record = r.read(SALT/'search-outcome.json.gz')
    salt_aliases = salt_record['aliases']
    unfinished = {k for k,v in rows.items() if not v['available']}
    assert len(unfinished)==222
    links, table = defaultdict(list), Counter()
    for k,row in rows.items():
        ref = coverage[k]
        identity = ref['observation']
        classified = classifications.get(k,{})
        basis = row.get('pressure_basis',{})
        assigned_pressure = ref['pressure_Pa'] if ref['bubble_multiplier'] is None else None
        actual = row.get('supplied_parent_pressure_Pa') or basis.get('search_pressure_Pa') or row.get('pressure_Pa') or assigned_pressure
        statuses = dict(below_bubble_421=k in below, unfinished=k in unfinished, descent=row['descent'],
                        confirmed=any(t['confirmed'] for t in classified.get('attempts',[])),
                        completed_without_descent=row['available'] and not row['descent'])
        table[tuple(statuses.values())]+=1
        observation = salt_data.get(identity)
        bubble = basis.get('model_bubble_pressure_Pa')
        src = observation['row'] if observation else {}
        declared = fit.get(identity)
        pressure_fields = [f for f in src if 'pressure' in f.casefold() or f in ('p_MPa','P_MPa','P_kPa')]
        links[identity].append(dict(key=k, pressure_Pa=actual, historical=ref, salt_basis=basis,
             same_calculation_as=salt_aliases.get(k), message=row.get('message'), **statuses,
             below_bubble_salt=actual<bubble if actual is not None and bubble is not None else None,
             source_and_assigned_pressure=dict(assigned_Pa=assigned_pressure,source_values={f:src[f] for f in pressure_fields}),
             observation=dict(group=observation['group'],role=observation['role'],unit=observation['unit'],
                              target=observation['observed'],value=observation['value'],status=observation['status'],
                              weight=declared['weight'] if declared else None) if observation else
                         dict(status='Phase search identity has no property row in retained #435 reduction')))
    sobrino = []
    for identity,x in salt_data.items():
        raw = x['row']
        if raw.get('source_key')=='Sobrino2016' and (i:=int(raw['source_row'])) in SOBRINO:
            frac,density = SOBRINO[i]
            assert (float(raw['MDEA_mass_fraction']),x['observed'],float(raw['pressure_MPa']),float(raw['temperature_K']))==(frac,density,.1,393.15)
            sibling, = [e for e in links[identity] if e['key'].endswith(':problem')]
            c = rows[sibling['key']]
            v = x['value']
            sobrino.append(dict(observation=x, fit_weight=fit[identity]['weight'], search=sibling,
                condition='Table 5 p.234 at 0.1 MPa; Anton Paar DMA HPM, expanded uncertainty <0.7 kg/m3',
                liquid_branch_error_kg_m3=v-density, salt_bubble_Pa=c.get('pressure_basis',{}).get('model_bubble_pressure_Pa'),
                original_cost=.5*fit[identity]['weight']*x['residual']**2))
    target = {}
    for case in ('salt','historical'):
        endpoint,_ = mdea_incumbent(case)
        rt = route(case,'B')
        transfer.coexistence_421.fixed(rt,rt.bind(endpoint))
        target[case] = rt.result('fixed-pressure.json')
        for attempt in target[case]['attempts']:
            attempt['failed_acceptance'] = [
                label for label,passed in dict(tolerance=attempt.get('requested_tolerance_met'),
                     positive=len(attempt.get('amounts_mol',[]))==2 and min(attempt['amounts_mol'])>0,
                     distinct=attempt.get('distinct'), roots=bool(attempt.get('roots')) and all(
                         any(q['returned']=='liquid' for q in matched(opts,1e-10)) for opts in attempt['roots']),
                     resolved_lowering=attempt.get('Gibbs_decrease_over_RT_mol',-math.inf)>
                                       attempt.get('numerical_error_over_RT_mol',math.inf)).items() if not passed]
    assert target['salt']['P_Pa']==target['historical']['P_Pa']
    historical_stability = MDEA.RESULTS/'stability.json'
    hist = r.read(historical_stability)
    doc = dict(seconds=monotonic()-start, wheel_sha256=r.SHA,
         parameter_sha256=r.s.sha256(source), joins=links, sobrinorows=sobrino,
         below_bubble_observations=sorted(below_observations),
         below_bubble_observation_counts=Counter(salt_data[i]['unit'] for i in below_observations),
         below_bubble_unfinished_observations=sorted({coverage[k]['observation'] for k in below & unfinished}),
         measured_aliases={k:v for k,v in salt_aliases.items() if k in rows},
         table_8_context=dict(historical_411=dict(
            sha256=r.s.sha256(historical_stability),states=hist['grid']['states'],available=hist['grid']['available'],
            descent=hist['grid']['descent'],split_count=hist['liquid_liquid_splits_among_completed_searches'],
            supplied_trial_counts=hist['grid']['supplied_trial_counts']),
            salt_435_confirmed=salt_record['confirmed'],salt_435_geometry_sha256=r.s.sha256(SALT/'search-0.json.gz')),
         below_bubble_421=sorted(below), unfinished_435=sorted(unfinished), intersection=sorted(below & unfinished),
         cross_tab=[dict(flags=k,count=v) for k,v in table.items()], targeted=target)
    admit_census(doc)


def admit_census(doc):
    started = monotonic()
    point, source = mdea_incumbent('salt')
    assert doc['parameter_sha256']==r.s.sha256(source)
    run = route('salt','B')
    spec = run.bind(point)
    states = {q['key']:q for q in run.states(spec)}
    fixed = [q for links in doc['joins'].values() for q in links if q['historical']['bubble_multiplier'] is None]
    # A retained alias shares the parent declaration, not just its reported T/loading.
    unique = {q['same_calculation_as'] or q['key']:q for q in fixed}
    keys = list(unique)
    pilot = keys[::20]
    readbacks = {}
    for batch in (pilot,[k for k in keys if k not in pilot]):
        tick = monotonic()
        for key in batch:
            link = unique[key]
            row = dict(T_K=link['historical']['T_K'],assigned_Pa=link['pressure_Pa'],bubble_Pa=None,
                       requested_tolerance_met=False)
            readbacks[key] = row
            try:
                item = run.stability_row(spec,dict(states[key],compressed=True),1.)
                assert item.problem.temperature.value==row['T_K'] and item.problem.pressure.value==row['assigned_Pa'], key
                assert item.pressure_reference.temperature.value==item.problem.temperature.value
                assert item.pressure_reference.feed.values==item.problem.feed.values
                row['feed_mol'] = dict(zip(spec.parameters.component_ids,item.problem.feed.values,strict=True))
                result = eq.solve_equilibrium(spec.model,item.pressure_reference)
                row.update(message=result.message,requested_tolerance_met=result.requested_tolerance_met,
                           result_pressure_Pa=result.pressure if math.isfinite(result.pressure) else None,
                           row_tolerance=item.pressure_reference.row_tolerance)
                if result.requested_tolerance_met and math.isfinite(result.pressure) and result.pressure>0:
                    row['bubble_Pa'] = result.pressure
            except (ValueError,RuntimeError) as error:
                row['message'] = f'{type(error).__name__}: {error}'
        if batch is pilot:
            pilot_seconds = monotonic()-tick
            projected = pilot_seconds*len(keys)/len(pilot)
            if projected>1200:
                save(WORK/'B/salt-bubble-pilot.json.gz',dict(rows=readbacks,pilot_seconds=pilot_seconds,
                     projected_seconds=projected))
                raise SystemExit(f'B salt bubble projection {projected:.1f} s exceeds 1200 s')
    for q in fixed:
        key = q['same_calculation_as'] or q['key']
        readback = readbacks[key]
        assert q['historical']['T_K']==readback['T_K'] and q['pressure_Pa']==readback['assigned_Pa']
        pressure = readback['bubble_Pa']
        q.update(salt_bubble_readback=key,below_bubble_salt=q['pressure_Pa']<pressure if pressure is not None else None)
    by_key = {q['key']:q for q in fixed}
    for row in doc['sobrinorows']:
        row['search'] = by_key[row['search']['key']]
        row['salt_bubble_Pa'] = readbacks[row['search']['salt_bubble_readback']]['bubble_Pa']
    observations = r.read(SALT/'data-rows.json.gz')
    doc['metrics'] = mdea_deviations(observations,doc['joins'])
    seconds = monotonic()-started
    doc['salt_bubble'] = dict(rows=readbacks,seconds=seconds,pilot_seconds=pilot_seconds,projected_seconds=projected)
    save(OUT/'B/census.json.gz',doc)
    print(f'B MDEA salt bubble {seconds:.2f} s (pilot projected {projected:.2f} s)',flush=True)


if __name__ == '__main__':
    a.study.reuse.bind_wheel()
    r.verify()
    if sys.argv[1]=='B-bubble':
        admit_census(r.read(OUT/'B/census.json.gz'))
    else:
        {'A':reference,'B':census}[sys.argv[1]]()
