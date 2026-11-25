"""Differentiate reconstructed extensive Gibbs energy on continued equilibrium branches."""
# ruff: noqa: E402
from copy import copy
from math import fsum, log
import sys
from time import monotonic

from refit import OUT, P_REF, configured, epcsaft, eq, fingerprint, np, put, r, reg
from classify_descents import DENSITY_WINDOW, ERROR_TERMS, matched, pressure_roots
from mdea_reference import seed_state
from phases import physical
from round_8.records import Sources
from verify_reference_calorics import first_actions, observable

R = epcsaft.GAS_CONSTANT_J_PER_MOL_K
R8 = OUT.parents[1] / 'round_8/results/C1-replays.json.gz'
FITTED = dict(MEA='monoethanolamine', DEA='diethanolamine', MDEA='methyldiethanolamine',
              AMP_free='aminomethylpropanol')


def anchored_offsets(anchor_model, thermal, declaration, T, unanchored):
    """Use the native reaction contractions and independently bind the neutral caloric gauge."""
    supplied = np.array([bool(x) for x in thermal.component_intervals])
    nu = np.array([q.stoichiometry for q in declaration.reactions])
    offsets = np.zeros(len(supplied))
    P0 = thermal.standard_pressure
    neutral = {}
    for i in np.flatnonzero(supplied):
        composition = np.zeros(len(supplied))
        composition[i] = 1.
        state = anchor_model.state(T,rho=P0/(R*T),x=composition,derived_properties=True)
        h,s = state.ideal_enthalpy,state.ideal_entropy
        if h is None or s is None:
            raise ValueError(f'Caloric anchor unavailable for {anchor_model.component_ids[i]}')
        offsets[i] = (h-T*s)/(R*T)+log(R*T/P0)
        neutral[anchor_model.component_ids[i]] = dict(h_J_mol=h,s_J_mol_K=s,offset_over_RT=offsets[i])
    # The retained neutral anchors determine the reference on all conserved
    # neutral components. The remaining charge gauge cancels in each phase.
    contraction = nu @ np.asarray(unanchored)
    offsets[~supplied] = np.linalg.lstsq(nu[:,~supplied],contraction-nu @ offsets,rcond=None)[0]
    return offsets,neutral,(nu @ offsets-contraction).tolist()


def solve(spec, model, anchor_model, thermal, declaration, seed=None):
    if seed is not None:
        phases = declaration.phases
        for i, phase in enumerate(phases):
            phase.composition_guess = [seed.phase_mole_fractions(i)[j] for j in phase.support]
            phase.packing_guess = seed.packing_fractions[i]
        declaration.phases = phases
    result = eq.solve_equilibrium(model, declaration, start=seed if seed and len(seed.amounts)==len(declaration.phases) else None)
    row = dict(T_K=result.temperature,P_Pa=result.pressure,solver=result.message,
               admitted=False, requested_tolerance_met=result.requested_tolerance_met)
    if not result.requested_tolerance_met:
        return row, result
    checks = physical(spec, declaration, result)
    continuation = []
    if any(k in model.component_ids for k in ('monoethanolamine','diethanolamine')):
        # Round 8 allowed five repeated warm reads when pressure closure was
        # obscured by cancellation in the low-pressure liquid branch.
        for _ in range(4):
            if checks['physical_checks_pass']:
                break
            phases = declaration.phases
            for i, phase in enumerate(phases):
                phase.composition_guess = [result.phase_mole_fractions(i)[j] for j in phase.support]
                phase.packing_guess = result.packing_fractions[i]
            declaration.phases = phases
            refined = eq.solve_equilibrium(model,declaration)
            observed = dict(message=refined.message,tolerance_met=refined.requested_tolerance_met)
            continuation.append(observed)
            if not refined.requested_tolerance_met:
                continue
            candidate = physical(spec,declaration,refined)
            observed['checks'] = candidate
            if (candidate['physical_checks_pass'] or
                max(abs(q['pressure_residual_Pa']) for q in candidate['phases']) <
                max(abs(q['pressure_residual_Pa']) for q in checks['phases'])):
                result,checks = refined,candidate
    row['convergence_message'] = result.message
    row['closure_refinement'] = continuation
    row.update(checks)
    T,P = result.temperature,result.pressure
    compiled = eq.compile_problem(model,declaration)
    standard = eq.stability_test(compiled, result)
    unanchored = standard.standard_over_rt
    b,neutral,contraction_error = anchored_offsets(anchor_model,thermal,declaration,T,unanchored)
    assert all(activity.reference_pressure_pa==P_REF for activity in eq.reaction_activities(model,result))
    values = []
    for i,(n,rho) in enumerate(zip(result.amounts,result.molar_densities,strict=True)):
        x = result.phase_mole_fractions(i)
        state = model.state(T,rho=rho,x=x)
        eos = n*R*T*(state.residual_helmholtz + P/(rho*R*T) - 1 + fsum(
            v*log(v*rho) for v in x if v>0))
        standard_g = n*R*T*fsum(v*bb for v,bb in zip(x,b,strict=True) if v>0)
        roots = pressure_roots(model,T,P,x,rho)
        admitted_roots = matched(roots,declaration.row_tolerance)
        continued_dense = (seed is not None and state.pressure_density_derivative>0
                           and abs(log(rho/seed.molar_densities[i]))<=DENSITY_WINDOW)
        values.append(dict(amount_mol=n,x=x,rho_mol_m3=rho,roots=roots,volume_m3=n/rho,
                           eos_G_J=eos,standard_G_J=standard_g,pressure_slope=state.pressure_density_derivative,
                           H_res_J=n*state.residual_enthalpy,
                           continued_dense=continued_dense,
                           liquid_root=any(q['returned']=='liquid' for q in admitted_roots),
                           energy_error_J=n*R*T*fsum(standard.present_phases[i][k] for k in ERROR_TERMS)))
    row.update(values=values,b=b,unanchored_b=unanchored,neutral_caloric_anchors=neutral,
               reaction_contraction_error_over_RT=contraction_error,
               G_J=fsum(q['eos_G_J']+q['standard_G_J'] for q in values),
               volume_m3=fsum(q['volume_m3'] for q in values),
               G_error_J=fsum(q['energy_error_J'] for q in values),reference_pressure_Pa=P_REF)
    row['admitted'] = (checks['physical_checks_pass'] and
                       all(q['amount_mol']>0 and (q['liquid_root'] or q['continued_dense']) for q in values))
    observables = [observable('SystemEnthalpy',0)]+[
        observable('PhaseProperty',i,prop=epcsaft.PropertyObservable.TotalEntropy) for i in range(len(values))]
    try:
        h,*entropy = [value for value,_ in first_actions(model,declaration,result,observables,
                                                        [(0.,0.,[0.]*len(b))])[0]]
        row.update(engine_H_J=h,engine_H_over_T_minus_S_J_K=h/T-fsum(
            s*q['amount_mol'] for s,q in zip(entropy,values,strict=True)))
    except (ValueError,RuntimeError) as error:
        row['caloric_refusal'] = str(error)
    return row,result


def derivatives(spec, model, thermal, problem, T, P, amine_feed, starting_solution=None):
    P0 = thermal.standard_pressure
    zero = epcsaft.IdealInterval(250.,500.,True,True,
        epcsaft.IdealCorrelation(epcsaft.IdealPolynomial([0.],350.,0.,0.),P0))
    # Native bulk ideal output requires intervals in every slot. The inserted
    # zero records have zero mole fraction in every pure-anchor call.
    anchor_model = epcsaft.Mixture(spec.parameters,thermochemistry=epcsaft.ThermochemistryRecord(
        P0,[q or [zero] for q in thermal.component_intervals]))
    center, seed = solve(spec,model,anchor_model,thermal,problem,starting_solution)
    record = dict(center=center,T_K=T,P_Pa=P,apparent_amine_feed_mol=amine_feed,steps=[])
    if 'G_J' not in center:
        return record
    for factor, dt in ((1e-4,.04),(5e-5,.02),(2.5e-5,.01)):
        dp = factor*P
        points = {}
        for label,t,p in (('P+',T,P+dp),('P-',T,P-dp),('T+',T+dt,P),('T-',T-dt,P)):
            try:
                problem.temperature = type(problem.temperature).fixed(t)
                problem.pressure = type(problem.pressure).fixed(p)
                points[label],_ = solve(spec,model,anchor_model,thermal,problem,seed)
            except (RuntimeError,ValueError) as error:
                points[label] = dict(T_K=t,P_Pa=p,admitted=False,refusal=str(error))
        row = dict(step_Pa=dp,step_K=dt,points=points)
        record['steps'].append(row)
        if all('G_J' in points[k] for k in ('P+','P-')):
            plus,minus = [points[k] for k in ('P+','P-')]
            volume = (plus['G_J']-minus['G_J'])/(2*dp)
            row.update(G_pressure_derivative_m3=volume,signed_volume_error_m3=volume-center['volume_m3'],
                       relative_volume_error=volume/center['volume_m3']-1,
                       volume_admitted=center['admitted'] and plus['admitted'] and minus['admitted'],
                       volume_arithmetic_error_m3=(plus['G_error_J']+minus['G_error_J'])/(2*dp))
        if all('G_J' in points[k] for k in ('T+','T-')):
            plus,minus = [points[k] for k in ('T+','T-')]
            b_T = [(x-y)/(2*dt) for x,y in zip(plus['b'],minus['b'],strict=True)]
            components = []
            neutral = [bool(x) for x in thermal.component_intervals]
            for phase in center['values']:
                offset_h = [-phase['amount_mol']*R*T*T*v*db for v,db in zip(phase['x'],b_T,strict=True)]
                # The ideal-density term uses ln(rho_i). The +nRT term and
                # each species standard's derivative give the ideal enthalpy.
                h_i = [phase['amount_mol']*R*T*v+h for v,h in zip(phase['x'],offset_h,strict=True)]
                components.append(dict(eos_residual_H_J=phase['H_res_J'],offset_H_by_species_J=offset_h,
                    neutral_caloric_H_J=fsum(h for h,anchor in zip(h_i,neutral,strict=True) if anchor),
                    reaction_completed_H_J=fsum(h for h,anchor in zip(h_i,neutral,strict=True) if not anchor),
                    pressure_chain_H_J=0.,eq12_H_J=phase['H_res_J']+fsum(h_i)))
            h = -T*T*(plus['G_J']/(T+dt)-minus['G_J']/(T-dt))/(2*dt)
            eq12 = fsum(q['eq12_H_J'] for q in components)
            row.update(fixed_reference_offset_temperature_derivative_per_K=b_T,caloric_components=components,
                       eq12_H_J=eq12,Gibbs_Helmholtz_H_J=h,eq12_minus_Gibbs_Helmholtz_J=eq12-h,
                       enthalpy_admitted=center['admitted'] and plus['admitted'] and minus['admitted'],
                       caloric_arithmetic_error_J=(T*T/(2*dt))*(
                           plus['G_error_J']/(T+dt)+minus['G_error_J']/(T-dt)))
            if 'engine_H_J' in center:
                row.update(engine_minus_Gibbs_Helmholtz_J=center['engine_H_J']-h,
                           engine_minus_eq12_J=center['engine_H_J']-eq12)
            if all('engine_H_over_T_minus_S_J_K' in q for q in (plus,minus)):
                row['H_over_T_minus_S_check_J'] = -T*T*(
                    plus['engine_H_over_T_minus_S_J_K']-minus['engine_H_over_T_minus_S_J_K'])/(2*dt)
    return record


def main(mode):
    r.verify()
    baseline = r.read(R8)['rows']
    for design,component in FITTED.items():
        started = monotonic()
        old = baseline[design.removesuffix('_free')]['value']
        run,point,_ = configured(design,'C1')
        if mode=='selected':
            selection_path = OUT/f'{design}/selection.json'
            if not selection_path.exists():
                continue
            selection = r.read(selection_path)
            if not selection['selected']:
                continue
            point = r.read(OUT/f"{design}/{selection['selected']}.json.gz")['endpoint']
            assert fingerprint(point)==selection['endpoint_fingerprint']
        record = dict(wheel=r.SHA,mode=mode,endpoint_fingerprint=fingerprint(point),
                      observation=old['observation'],tracking_pressure_Pa=old['P_Pa'])
        try:
            spec = run.bind(point)
            model = spec.model
            thermal = spec.thermal
            if design=='AMP_free':
                # Round-8 declared gauge for the absent AMP caloric anchor.
                P0 = spec.thermal.standard_pressure
                zero = epcsaft.IdealInterval(250.,500.,True,True,
                    epcsaft.IdealCorrelation(epcsaft.IdealPolynomial([0.],350.,0.,0.),P0))
                neutral = ('water','carbon-dioxide',component)
                thermal = epcsaft.ThermochemistryRecord(
                    P0,[[zero] if k in neutral else [] for k in spec.parameters.component_ids])
                model = epcsaft.Mixture(spec.parameters,thermochemistry=thermal)
                record['caloric_basis'] = dict(gauge='Round 8 zero Cp, h and s for neutral species',
                                               reference_temperature_K=350.,reference_pressure_Pa=P0)
            row = next(q for q in spec.inputs['observations']['fitted'] if q['identity']==old['observation'])
            bubble = copy(spec.problems[row['problem']])
            result = eq.solve_equilibrium(model,bubble)
            if not result.requested_tolerance_met:
                raise ValueError(result.message)
            problem = copy(bubble)
            liquid = copy(problem.phases[0])
            liquid.amount = eq.Free()
            liquid.composition_guess = result.phase_mole_fractions(0)
            liquid.packing_guess = result.packing_fractions[0]
            problem.phases = [liquid]
            problem.P = result.pressure
            native = reg.stability(spec.parameters,problem,scale=1.).problem
            record.update(derivatives(spec,model,thermal,native,result.temperature,result.pressure,old['amine_feed_mol'],result))
        except (AttributeError,RuntimeError,ValueError,AssertionError) as error:
            record['refusal'] = f'{type(error).__name__}: {error}'
        name = f'C1/{mode}-{design}.json.gz'
        if (OUT/name).exists():
            record['prior_attempt'] = r.read(OUT/name)
        put(name,dict(record,seconds=monotonic()-started))


def high_pressure(mode):
    from phase_replays import incumbent_pair, point_for

    if mode=='selected' and not (OUT/'MDEA/selection.json').exists():
        return
    try:
        run,point = point_for('MDEA',mode,'C1-high-pressure')
    except (TypeError,ValueError):
        return
    spec = run.bind(point)
    old = Sources().core('C/salt/search-outcome.json.gz')
    entry, = [q for q in old['classifications'] if q['key'] in old['confirmed']]
    seed = incumbent_pair(entry)
    state = seed_state(spec,entry)
    T,P = state['T'],entry['pressure_Pa']
    for index, label in enumerate(('parent','daughter-1','daughter-2'),start=-1):
        started = monotonic()
        problem = run.stability_row(spec,state,1.).problem
        problem.pressure = type(problem.pressure).fixed(P)
        n = state['stock']['methyldiethanolamine']
        if index>=0:
            amount,x = seed['amounts_mol'][index],seed['phases'][index]
            inventory = problem.feed
            inventory.values = [amount*v for v in x]
            problem.feed = inventory
            phase = problem.phases[0]
            phase.composition_guess,phase.packing_guess = x,seed['packings'][index]
            problem.phases = [phase]
            # The paired inventories retain normalization to the total parent
            # apparent amine feed so their extensive contributions can be added.
        record = dict(endpoint_fingerprint=fingerprint(point),mode=mode,wheel=r.SHA,
                      pressure_basis='retained absolute pressure',branch=label,feed_mol=list(problem.feed.values),
                      inventory_basis='retained split daughter inventory' if index>=0 else 'retained parent feed')
        try:
            record.update(derivatives(spec,spec.model,spec.thermal,problem,T,P,n))
        except (AttributeError,RuntimeError,ValueError,AssertionError) as error:
            record['refusal'] = f'{type(error).__name__}: {error}'
        put(f'C1/{mode}-MDEA-{label}.json.gz',dict(record,seconds=monotonic()-started))


if __name__=='__main__':
    from refit import a
    a.study.reuse.bind_wheel()
    main(sys.argv[1])
    high_pressure(sys.argv[1])
