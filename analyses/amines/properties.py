"""Derivative and property readbacks at one declared endpoint."""

import copy
import json
from math import fsum, log
from types import SimpleNamespace

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
from .records import RESULTS, read
from MEA.solvent_specification import conditional_information, deviation_statistics

from .model import P_REF, calculation_declaration
from .phase import DENSITY_WINDOW, ERROR_TERMS, R, matched, physical, pressure_roots
from .wheel import ROOT, verify


def write_gibbs_derivative_summary():
    wheel = verify()
    folder = RESULTS / "shared/comparisons/properties/derivatives"
    paths = {path.name.removesuffix(".json.gz"): path
             for base in (folder, folder / "rebuild-441") for path in base.glob("*.json.gz")}
    records = {name: read(path) for name, path in sorted(paths.items(), key=lambda item: item[1].name)}
    if any(record["wheel"] != wheel for record in records.values()):
        raise ValueError("Gibbs derivative record uses another wheel")

    rows = []

    def summarize(name, inputs, comparison, admitted_field, discrepancy, arithmetic):
        record = records[inputs[0]]
        matching = ("T_K", "P_Pa", "endpoint_fingerprint", "apparent_amine_feed_mol")
        if any(records[key][field] != record[field] for key in inputs for field in matching):
            raise ValueError(f"Different conditions for the daughter inventories of {name}")
        candidates = []
        for steps in zip(*(records[key]["steps"] for key in inputs), strict=True):
            if all(discrepancy in step for step in steps):
                candidates.append((sum(step[discrepancy] for step in steps),
                                   sum(step[arithmetic] for step in steps),
                                   all(step.get(admitted_field) for step in steps)))
        admitted = [candidate for candidate in candidates if candidate[2]]
        used = admitted or (candidates if len(inputs) == 1 else [])
        if not used:
            return
        delta, arithmetic_error, _ = used[-1]
        span = max(step[0] for step in used) - min(step[0] for step in used)
        error = arithmetic_error + span
        scale = 1 if comparison == "volume" else record["apparent_amine_feed_mol"]
        rows.append(dict(
            state=name, comparison=comparison, temperature_K=record["T_K"], pressure_Pa=record["P_Pa"],
            pressure_basis=record.get("pressure_basis"),
            signed_error=delta / scale, estimated_error=error / scale, admitted_steps=len(admitted),
            disposition=("agreement within numerical error"
                         if len(admitted) >= 2 and abs(delta) <= error else "undecided"),
            records=[paths[key].relative_to(ROOT).as_posix() for key in inputs],
        ))
        if comparison == "volume" and len(inputs) == 1:
            volume = record["center"]["volume_m3"]
            rows[-1].update(relative_error=delta / volume, relative_estimated_error=error / volume)

    states = [(name, [name]) for name, record in records.items() if record.get("steps")]
    states.extend((f"{mode} MDEA daughter-inventory sum", [f"{mode}-MDEA-daughter-{i}" for i in (1, 2)])
                  for mode in ("fixed-at-old", "selected"))
    for state, inputs in states:
        summarize(state, inputs, "volume", "volume_admitted",
                  "signed_volume_error_m3", "volume_arithmetic_error_m3")
        summarize(state, inputs, "Eq. 12", "enthalpy_admitted",
                  "eq12_minus_Gibbs_Helmholtz_J", "caloric_arithmetic_error_J")
    path = ROOT / "analyses/amines/results/shared/properties/gibbs-derivatives.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(wheel=wheel, rows=rows), indent=2) + "\n")


def endpoint_diagnostics(spec, fit_replay, point, controls):
    verify()
    declared = point["coordinates"]
    native = spec.coordinates()
    rows = spec.inputs["observations"]["fitted"]
    ev = reg.differentiate(
        spec.parameters,
        native,
        [spec.observation(q) for q in rows],
        optimizer=[0.0] * len(native),
        thermochemistry=spec.thermal,
    )
    values = dict(derivative_statuses=[q.name for q in ev.statuses])
    if fit_replay["cost"] is None or any(q.name != "Available" for q in ev.statuses):
        return values
    residual = np.array([q["weighted_residual"] for q in fit_replay["rows"]])
    J = spec.whiten(np.array(ev.residual_optimizer_gradient).reshape(len(rows), len(native)))
    scale = np.array([q.scale for q in native])
    width = np.array([q.upper - q.lower for q in native])
    grad = (J * (width / scale)).T @ residual
    projected = grad.copy()
    active = {}
    for i, q in enumerate(native):
        side = (
            "lower"
            if q.origin - q.lower <= 1e-6 * q.scale
            else "upper"
            if q.upper - q.origin <= 1e-6 * q.scale
            else None
        )
        if side:
            active[declared[i]["identity"]] = side
            if (side == "lower" and grad[i] > 0) or (side == "upper" and grad[i] < 0):
                projected[i] = 0.0
    lower, upper = (np.array([getattr(q, k) - q.origin for q in native]) / scale for k in ("lower", "upper"))
    optimizer_norm = float(np.max(np.abs(np.clip(-grad * scale / width, lower, upper))))
    values.update(
        jacobian_bound_normalized=(J * (width / scale)).tolist(),
        gradient=grad.tolist(),
        projected_gradient=projected.tolist(),
        projected_gradient_inf=float(np.max(np.abs(projected))),
        active_bounds=active,
        optimizer_projected_gradient_inf=optimizer_norm,
        stationarity_met=optimizer_norm <= controls["gradient_tolerance"],
        maximum_prediction_relative_difference=max(
            abs(v - q["value"]) / max(1.0, abs(q["value"]))
            for v, q in zip(ev.predictions, fit_replay["rows"], strict=True)
        ),
    )
    ids = [q["identity"] for q in declared]
    result = SimpleNamespace(
        physical=[q.origin for q in native],
        covariance=SimpleNamespace(active_bounds=[ids.index(i) for i in active]),
    )
    try:
        values["uncertainty"] = conditional_information(
            result,
            J / scale,
            residual,
            ids,
            [q.lower for q in native],
            [q.upper for q in native],
        )
    except np.linalg.LinAlgError as exc:
        values["uncertainty_refusal"] = str(exc)
    return values


def marks(route, T, problem=None):
    used = {r.name for r in problem.reactions} if problem is not None else set(route.config["reaction_ranges_K"])
    ranges = route.config["reaction_ranges_K"]
    return {
        name: (
            "reaction not used"
            if name not in used
            else "source range unknown"
            if ranges.get(name) is None
            else "temperature unavailable"
            if T is None
            else not ranges[name][0] <= T <= ranges[name][1]
        )
        for name in used | ranges.keys()
    }


def property_rows(route, point, fitted=None):
    spec, predictions = route.bind(point), []
    fitted = {} if fitted is None else {row["identity"]: row for row in fitted}
    for role in ("fitted", "comparisons"):
        for record in spec.inputs["observations"][role]:
            prediction = fitted.get(record["identity"]) if role == "fitted" else None
            if prediction is None:
                prediction = spec.prediction(record)
            problem = spec.problems[record.get("problem", record.get("initial"))]
            key = json.dumps(calculation_declaration(problem), sort_keys=True) if isinstance(problem.T, eq.Free) else None
            predictions.append((role, record, problem, key, prediction))
    # The paired boiling-temperature and vapor-composition observations have the same problem declaration.
    temperatures = {
        key: prediction["value"]
        for _, record, _, key, prediction in predictions
        if key is not None and record.get("kind") == "temperature" and prediction["status"] == "Available"
    }
    output = []
    for role, record, problem, key, prediction in predictions:
        T = temperatures.get(key) if key is not None else problem.T
        output.append(dict(
            prediction,
            role=record.get("role", "fitted" if role == "fitted" else "not fitted"),
            T_K=T,
            outside_ranges=marks(route, T, problem),
        ))
    summary = []
    for group, role, unit in sorted({(r["group"], r["role"], r.get("unit") or "unit unspecified") for r in output}):
        for name in {name for r in output for name in r["outside_ranges"]}:
            dispositions = [False, True, "source range unknown", "reaction not used"]
            if any(r["outside_ranges"].get(name) == "temperature unavailable" for r in output):
                dispositions.append("temperature unavailable")
            for outside in dispositions:
                rows = [
                    r
                    for r in output
                    if (
                        r["group"],
                        r["role"],
                        r.get("unit") or "unit unspecified",
                        r["outside_ranges"].get(name, "reaction not used"),
                    )
                    == (group, role, unit, outside)
                ]
                pairs = [
                    (r["observed"], r["value"])
                    for r in rows
                    if r.get("value") is not None and r.get("status") == "Available"
                ]
                summary.append(
                    dict(
                        group=group,
                        role=role,
                        unit=unit,
                        range_name=name,
                        outside_range=outside,
                        rows=len(rows),
                        available=len(pairs),
                        statistics=deviation_statistics(pairs, unit) if pairs else None,
                    )
                )
    return dict(rows=output, deviations=summary, wheel=verify())


def curve_rows(route, point, declarations=None):
    spec, output = route.bind(point), []
    for row in route.load(route.config["curve_rows"]) if declarations is None else declarations:
        record = copy.deepcopy(row["observation"])
        for key, declaration in row["problems"].items():
            spec.problems[key] = spec.problem(declaration["template"], declaration["bindings"])
        record.update(
            observation_parameters=spec.parameter_sha256,
            temperature_domain=route.config["calculation_interval_K"],
        )
        T = spec.problems[record.get("problem", record.get("initial"))].T
        assert route.config["calculation_interval_K"][0] <= T <= route.config["calculation_interval_K"][1]
        output.append(
            dict(
                spec.prediction(record),
                curve=row["curve"],
                loading=row["loading"],
                T_K=T,
                outside_ranges=marks(
                    route,
                    T,
                    spec.problems[record.get("problem", record.get("initial"))],
                ),
            )
        )
    return dict(rows=output, wheel=verify())


def observable(kind: str, phase: int, component: int = 0, prop: object | None = None) -> object:
    kind_value = getattr(eq.SolvedStateObservableKind, kind)
    if prop is None:
        return eq.SolvedStateObservable(kind_value, phase, component)
    return eq.SolvedStateObservable(kind_value, phase, component, prop)


def first_actions(model: object, problem: object, result: object, observables: list, directions: list) -> list:
    width = len(model.component_ids)
    batches = eq.solved_state_first_actions(eq.compile_problem(model, problem), result, observables, [
        eq.SolvedStateActionDirection(d_t, d_p, feed or [0.0] * width, []) for d_t, d_p, feed in directions])
    for batch in batches:
        for item in batch.results:
            if item.status.name != "Available":
                raise RuntimeError(f"{item.observable}: {item.status.name} {item.diagnostic_message}")
    return [[(item.value, item.action) for item in batch.results] for batch in batches]


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
    row['convergence_message'] = result.message
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


def worked_state(spec, model, thermal, observation, amine_feed):
    """Continue the liquid branch of a fitted bubble state for C1."""
    row = next(q for q in spec.inputs['observations']['fitted'] if q['identity']==observation)
    bubble = copy.copy(spec.problems[row['problem']])
    result = eq.solve_equilibrium(model,bubble)
    if not result.requested_tolerance_met:
        raise ValueError(result.message)
    problem = copy.copy(bubble)
    liquid = copy.copy(problem.phases[0])
    liquid.amount = eq.Free()
    liquid.composition_guess = result.phase_mole_fractions(0)
    liquid.packing_guess = result.packing_fractions[0]
    problem.phases = [liquid]
    problem.P = result.pressure
    native = reg.stability(spec.parameters,problem,scale=1.).problem
    return derivatives(spec,model,thermal,native,result.temperature,result.pressure,amine_feed,result)


def worked_calorimetry(spec, record):
    """Replay the recorded addition enthalpy and heat-capacity stencil."""
    verify()
    T, P = record["T_K"], record["P_Pa"]
    cp_row = next(row for row in spec.inputs["observations"]["fitted"] if row["group"] == "Cp")
    template = spec.problems[cp_row["problem"]]
    problems = {}
    values = {}
    for label, retained in record["points"].items():
        problem = copy.copy(template)
        problem.T, problem.P = retained["T_K"], P
        problem.feed = eq.Amounts(dict(zip(spec.parameters.component_ids, retained["feed_mol"], strict=True)))
        result = eq.solve_equilibrium(spec.model, problem)
        checks = physical(spec, problem, result) if result.requested_tolerance_met else {}
        if not checks.get("physical_checks_pass"):
            raise ValueError(f"Caloric state {label} failed closure: {result.message}")
        kinds = [observable("SystemEnthalpy", 0)]
        if label == "loaded":
            kinds.append(observable("EquilibriumIsobaricHeatCapacity", 0))
        values[label] = [value for value, _ in first_actions(spec.model, problem, result, kinds, [(0., 0., None)])[0]]
        problems[label] = problem
    added = record["added_CO2_mol"]
    observation = reg.addition_enthalpy(spec.parameters, problems["initial"], problems["loaded"],
        {"carbon-dioxide": 1.0}, added, T, P, phase="vapor", observed=0.0, form="difference", scale=1.0)
    prediction = reg.predict(spec.model, observation)
    if prediction.status.name != "Available" or not prediction.requested_tolerance_met:
        raise ValueError(prediction.message)
    amount = fsum(record["apparent_feed_mol"])
    finite = [(values[str(step)][0] - values[str(-step)][0]) / (2 * step * amount)
              for step in record["stencil_steps_K"]]
    return dict(heat_kJ_mol=prediction.value / 1000, cp_J_mol_K=values["loaded"][1], cp_stencil_J_mol_K=finite)
