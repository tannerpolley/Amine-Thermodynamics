"""Replay the AMP stability and MEA caloric examples on the pinned wheel (#428)."""
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import tomllib

from part_ii import ROOT, SHA, SHARED, Route, calculation_declaration, epcsaft, eq, np, reg, stable
from amp_transfer import classify_descents as cd
from fit_observations import heat_items
from heat_evidence_170 import hc, request, s, vrc

BUNDLE = ROOT / 'analyses/mea_parameter_bundle'
R = epcsaft.GAS_CONSTANT_J_PER_MOL_K


def identity(*paths):
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def phase(model, T, P, amounts, rho, x, formulas):
    eos = model.state(T, rho=rho, x=x)
    return dict(amount_mol=amounts, density_mol_m3=rho, x=x, pressure_Pa=eos.pressure,
                pressure_residual_Pa=eos.pressure-P, normalization_residual=math.fsum(x)-1,
                charge_residual=math.fsum(w*f['charge'] for w, f in zip(x, formulas, strict=True)))


def balances(feed, phases, formulas):
    inventory = sum(p['amount_mol']*np.array(p['x']) for p in phases)
    counts = np.array([[f.get(e, 0) for f in formulas] for e in 'CHNO'])
    atoms = counts @ (inventory-feed)
    scaled = atoms/(math.fsum(feed)*counts.max(axis=1))
    return dict(element_residual_mol=dict(zip('CHNO', atoms.tolist(), strict=True)), scaled_element_residual=dict(zip('CHNO', scaled.tolist(), strict=True)))


def phase_passed(p, P, tol):
    return max(abs(p['pressure_residual_Pa'])/P, abs(p['charge_residual']), abs(p['normalization_residual'])) <= tol


def amp(run):
    folder = ROOT / 'analyses/amp_transfer'
    declaration = folder / 'inputs/retransfer-344/phase-2/AMP-05e94210.json'
    main = folder / 'results/retransfer-412-f2-05e94210/main'
    params, search, classification = (main / n for n in ('parameters.json', 'search-1.json.gz', 'phase-classification-1.json.gz'))
    inputs = identity(declaration, declaration.with_name('specification.toml'), params, search, classification, SHARED)
    assert inputs[str(params.relative_to(ROOT))] == 'd69f7e9df46d73662e1180713ae05bed7a32412fa7032920cf7139b0d88132dd'
    route = Route(declaration, run)
    route.check_run_output()
    spec = route.bind(stable.read(params))
    stock = {'water': 11.545384436618988, 'aminomethylpropanol': 1.0}
    T, loading, ratio = 393.15, 0.7, 1.05
    key = f'grid:{stock}:{T}:{loading}:{ratio}'
    retained = next(r for r in stable.read(search) if r['key'] == key)
    split = next(r for r in stable.read(classification)['states'] if r['key'] == key)
    seed = next(a for a in split['attempts'] if a['confirmed'])
    item = route.stability_row(spec, dict(stock=stock, T=T, a=loading, c=ratio), 1.)
    model = spec.model
    prediction = reg.predict(model, item)
    parent, P = item.problem, split['pressure_Pa']
    parent.pressure = type(parent.pressure).fixed(P)
    result = eq.solve_equilibrium(model, parent)
    compiled = eq.compile_problem(model, parent)
    report = prediction.stability.report
    trial = min((t for t in report.trials if t.resolved_descent and t.quantities.get('density_side') == 2
                 and len(t.phase.support) == 9), key=lambda t: t.quantities['tpd_over_rt'])
    q, w = trial.quantities, trial.composition
    D, error = q['tpd_over_rt'], q['plane_value_error_estimate_over_rt']
    plane = math.fsum(x*p for x, p in zip(w, report.plane_over_rt, strict=True))
    distance = q['g_over_rt']-plane
    witness, = (r for r in split['supplied_pressure_roots'] if r.get('reclosed_evidence') == 'evaluated')
    source = witness['witness']['phase']
    root = min(cd.matched(witness['roots'], parent.row_tolerance), key=lambda r: r['log_density_distance'])
    points, *_ = stable._applicable(item, [dict(source, packing=witness['reclosed_quantities']['packing_fraction'])], set(source['support']))
    options = eq.StabilityOptions()
    options.prepared_trials = eq.prepare_supplied_trials(model, T, points)
    supplied, = eq.stability_test(compiled, result, options).trials
    parent_g = cd.gibbs(compiled, result)
    pair = cd.coexistence(spec, parent, parent_g, list(zip(seed['phases'], seed['packings'], strict=True)))
    objective_delta = pair['objective_over_RT_mol']-result.objective
    gibbs_delta = pair['Gibbs_sum_over_RT_mol']-parent_g[0]
    paired_error = pair['numerical_error_over_RT_mol']
    species = list(spec.parameters.component_ids)
    formulas = [spec.spec['element_formulas'][c] for c in species]
    feed, tol = parent.feed.values, parent.row_tolerance
    phases = [phase(model, T, P, result.amounts[0], result.molar_densities[0], result.phase_mole_fractions(0), formulas)]
    phases += [phase(model, T, P, n, rho, x, formulas) for rho, n, x in sorted(
        zip(pair['densities_mol_m3'], pair['amounts_mol'], pair['phases'], strict=True))]
    trial_phase = phase(model, T, P, 1., 1/q['volume_m3_per_mol'], w, formulas)
    balance = [balances(feed, part, formulas) for part in (phases[:1], phases[1:])]
    checks = dict(optimized=(D == prediction.value == retained['value'] and error == prediction.stability.uncertainty == retained['uncertainty']
                             and distance < -error and abs(distance-D) <= error and any(r['composition'] == w for r in retained['witnesses'])),
                  supplied=(supplied.evidence == 'evaluated' and root['returned'] == 'liquid'
                            and supplied.quantities['tpd_over_rt'] < -error
                            and abs(supplied.quantities['tpd_over_rt']-witness['reclosed_quantities']['tpd_over_rt']) <= error),
                  split=(pair['confirmed'] and gibbs_delta < -paired_error and abs(gibbs_delta-objective_delta) <= paired_error),
                  equilibrium=result.requested_tolerance_met and pair['requested_tolerance_met'],
                  phase=all(phase_passed(p, P, tol) for p in [*phases, trial_phase]),
                  balances=all(abs(v) <= tol for b in balance for v in b['scaled_element_residual'].values()),
                  bubble=prediction.pressure_reference.value == retained['pressure_Pa'] and P == ratio*retained['pressure_Pa'])
    return dict(inputs=inputs, row_key=key, declaration=calculation_declaration(parent), solver_settings=result.solver_settings,
                species=species, T_K=T, P_Pa=P, bubble_Pa=retained['pressure_Pa'], feed_mol=feed, AMP_wt_percent=30., loading=loading,
                phases=phases, balances=balance, parent_residuals=result.residuals, split=pair, trial=trial_phase, trial_quantities=q,
                standard_over_rt=report.standard_over_rt, plane_over_rt=report.plane_over_rt, plane_contraction=plane, D_readback=distance,
                uncertainty=prediction.stability.uncertainty, supplied=dict(root=root, quantities=supplied.quantities),
                parent_G_RT_mol=parent_g[0], parent_objective_over_RT_mol=result.objective, Gibbs_difference_over_RT_mol=gibbs_delta,
                objective_difference_over_RT_mol=objective_delta, Gibbs_minus_objective_mol=gibbs_delta-objective_delta,
                outside_source_ranges=split['outside_ranges'], checks=checks)


def mea():
    params = BUNDLE / 'results/selected-current-best-parameters.json'
    earlier = BUNDLE / 'results/paper-evidence-341/paper-evidence/model-curves/heat.csv'
    declaration = ROOT / 'analyses/solvent_specification_mea/declarations.toml'
    inputs = identity(params, earlier, declaration, vrc.PHYSICAL_CALORICS, s.STATE_PACKET)
    assert inputs[str(params.relative_to(ROOT))] == 'ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed'
    mapping = s.parameter_mapping(params)
    parameters = epcsaft.Parameters.from_mapping(mapping)
    model = epcsaft.Mixture(parameters, thermochemistry=vrc.record())
    T, P, added = 313.15, 1734000., .31
    observation, = heat_items(mapping, parameters, [dict(temperature_K=T, system_pressure_Pa=P, alpha_final=added,
        observed_addition_enthalpy_J_per_mol_CO2=0., uH_J_per_mol_CO2=1.)], request(mapping, T, .11))
    prediction = reg.predict(model, observation)
    gas = model.state(T, P=P, x=observation.composition, phase='vapor')
    stream = vrc.co2_gas_enthalpy(T)+gas.residual_enthalpy
    element_formulas = tomllib.loads(declaration.read_text())['element_formulas']
    formulas = [element_formulas[c] for c in s.COMPONENT_IDS]
    initial, loaded = observation.problem, observation.final_problem
    feed, tol, p0 = loaded.feed.values, loaded.row_tolerance, vrc.CALORICS['reference_pressure_pa']
    masses = [c['fixed']['molar_mass']['value']['magnitude'] for c in mapping['components']]
    mass = math.fsum(n*m for n, m in zip(feed, masses, strict=True))
    points, checks = {}, {}
    for label, problem, temp in [('initial', initial, T), ('loaded', loaded, T),
                                  *((str(d), loaded, T+d) for step in hc.STEP_K for d in (-step, step))]:
        problem.temperature = type(problem.temperature).fixed(temp)
        result = eq.solve_equilibrium(model, problem)
        rho, = result.molar_densities
        n, = result.amounts
        x = result.phase_mole_fractions(0)
        row = phase(model, temp, P, n, rho, x, formulas)
        row.update(balances(problem.feed.values, [row], formulas))
        roots = cd.pressure_roots(model, temp, P, x, rho)
        row.update(T_K=temp, roots=roots, feed_mol=problem.feed.values, residuals=result.residuals, solver_settings=result.solver_settings)
        checks[label] = (result.success and result.requested_tolerance_met and phase_passed(row, P, tol)
                         and any(r['returned'] == 'liquid' for r in cd.matched(roots, tol))
                         and max(map(abs, row['scaled_element_residual'].values())) <= tol)
        (row['H_J'], _), = vrc.first_actions(model, problem, result, [vrc.observable('SystemEnthalpy', 0)], [(0., 0., None)])[0]
        if label != 'initial':
            quotients = eq.reaction_activities(model, result)
            row['ln_Q_pressure_standard'] = [a.log_pressure_quotient+sum(rx.stoichiometry)*math.log(a.standard_pressure_pa/p0)
                                             for a, rx in zip(quotients, problem.reactions, strict=True)]
        if label == 'loaded':
            (cp, _), = vrc.first_actions(model, problem, result, [vrc.observable('EquilibriumIsobaricHeatCapacity', 0)], [(0., 0., None)])[0]
            actions = vrc.first_actions(model, problem, result, [vrc.observable('PhaseLogActivity', 0, i)
                                        for i in range(len(s.COMPONENT_IDS))], [(1., 0., None)])[0]
            central, source = row, quotients
        points[label] = row
    finite = [(points[str(d)]['H_J']-points[str(-d)]['H_J'])/(2*d*sum(feed)) for d in hc.STEP_K]
    checks['heat_capacity'] = abs(cp-finite[1]) <= min(hc.RESOLVE_RTOL*abs(finite[1]), abs(cp-finite[0])/2)
    reactions = []
    for i, (rx, a) in enumerate(zip(loaded.reactions, source, strict=True)):
        law, nu = rx.correlation, rx.stoichiometry
        dnu = sum(nu)
        molality = (dnu-nu[vrc.WATER])*math.log(masses[vrc.WATER]*loaded.neutral_reference.standard_molality_mol_per_kg)
        ln_k = law.a+law.b/T+law.c*math.log(T/law.reference_temperature)+law.d*T+law.e/T**2+law.f*T**2
        source_slope = -law.b/T**2+law.c/T+law.d-2*law.e/T**3+2*law.f*T
        slope = math.fsum(n*d for n, (_, d) in zip(nu, actions, strict=True))+dnu/T
        factor = R*T*T/1000
        dh = factor*slope
        stencil = [factor*(points[str(d)]['ln_Q_pressure_standard'][i]-points[str(-d)]['ln_Q_pressure_standard'][i])/(2*d) for d in hc.STEP_K]
        checks[rx.name] = (abs(a.log_quotient-ln_k) <= tol and format(stencil[1], '.2f') == format(dh, '.2f')
                           and a.reference_pressure_pa == a.standard_pressure_pa == ([P]*3+[p0]*2)[i])
        reactions.append(dict(name=rx.name, P_source_Pa=a.reference_pressure_pa, ln_K_source=ln_k, ln_Q_source=a.log_quotient,
                              ln_Q_minus_ln_K_source=a.log_quotient-ln_k, molality_term=molality,
                              Gamma=a.log_pressure_quotient-a.log_quotient-molality, ln_K_ideal_gas=central['ln_Q_pressure_standard'][i],
                              source_kJ_mol=factor*source_slope, fugacity_kJ_mol=factor*(slope-source_slope),
                              ideal_gas_kJ_mol=dh, density_standard_kJ_mol=dh-dnu*R*T/1000, stencil_kJ_mol=stencil))
    with earlier.open() as stream_file:
        previous = next(r for r in csv.DictReader(stream_file) if (float(r['temperature_K']), float(r['pressure_Pa']), float(r['analytical_loading'])) == (T, P, added))
    heat = (central['H_J']-points['initial']['H_J']-added*stream)/added/1000
    checks['addition_heat'] = prediction.status.name == 'Available' and format(heat, '.8f') == format(prediction.value/1000, '.8f')
    loaded.temperature = type(loaded.temperature).fixed(T)
    return dict(inputs=inputs, T_K=T, P_Pa=P, P_standard_Pa=p0, species=list(s.COMPONENT_IDS), apparent_feed_mol=feed,
                MEA_wt_percent=30., loading_initial=0., loading_final=added, added_CO2_mol=added, loaded_mass_kg=mass,
                declaration=calculation_declaration(loaded), added_stream=dict(x=observation.composition, branch=observation.branch.name,
                density_mol_m3=gas.molar_density, eos_pressure_Pa=gas.pressure, H_J_per_mol=stream),
                points=points, heat_kJ_mol=heat, predicted_heat_kJ_mol=prediction.value/1000, earlier_row=previous,
                heat_minus_earlier_kJ_mol=heat-float(previous['value']), cp_J_mol_K=cp, cp_J_K=cp*sum(feed),
                cp_stencil_J_mol_K=finite, cp_minus_fine_J_mol_K=cp-finite[1], cp_kJ_kg_K=cp*sum(feed)/mass/1000,
                stencil_steps_K=hc.STEP_K, reactions=reactions, checks=checks)


if __name__ == '__main__':
    run = Path(sys.argv[1]).resolve()
    for name, calculate in (('amp', lambda: amp(run)), ('mea', mea)):
        record = calculate()
        (run / f'{name}.json').write_text(json.dumps(dict(wheel_sha256=SHA, **record), indent=2, allow_nan=False)+'\n')
        assert all(record['checks'].values()), record['checks']
