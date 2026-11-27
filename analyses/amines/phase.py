"""Declared phase requests and classification of the existing search evidence."""

import copy
from collections import Counter
from collections.abc import Mapping
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
import json
import math
import os
from types import SimpleNamespace

import numpy as np

from .model import calculation_declaration
from .wheel import verify

import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from MEA.solvent_specification import jsonable, stability_payload, supplied_negative

LOWEST_LOADING = 1e-5
FINITE_NEGATIVE = "no descent in the finite search"


def capped_feed(spec, record, parent):
    """Follow the declared loading nodes to the first rising pressure bracket."""
    from scipy.optimize import brentq

    args = record["arguments"]
    bubble = copy.copy(spec.problems[record["bubble"]])
    initial = parent.feed.values
    direction = {c: args["basis_amount"] * args["feed"].get(c, 0.0) for c in initial}
    action = eq.SolvedStateActionDirection(0.0, 0.0, [direction.get(c, 0.0) for c in spec.parameters.component_ids], [])
    observable = eq.SolvedStateObservable(eq.SolvedStateObservableKind.Pressure)
    nodes = []

    def solve(loading, start):
        bubble.feed = eq.Amounts({c: n + loading * direction[c] for c, n in initial.items()})
        result = eq.solve_equilibrium(spec.model, bubble, start=start)
        if not result.requested_tolerance_met:
            raise ValueError(f"Saturation bracket at loading {loading}: {result.message}")
        return result

    previous, start = None, None
    for loading in args["loading_grid"]:
        result = solve(loading, start)
        compiled = eq.compile_problem(spec.model, bubble)
        (slope,) = eq.solved_state_first_actions(compiled, result, [observable], [action])[0].results
        if slope.status.name != "Available":
            raise ValueError(f"Saturation bracket slope at {loading}: {slope.status.name}")
        nodes.append(dict(loading=loading, pressure_Pa=result.pressure, slope_Pa=slope.action))
        if (
            previous is not None
            and previous["pressure_Pa"] <= args["P"] < result.pressure
            and min(previous["slope_Pa"], slope.action) > 0
        ):
            bracket = [previous["loading"], loading]

            def residual(a):
                return solve(a, start).pressure - args["P"]

            root = brentq(residual, *bracket, xtol=1e-14)
            capped = min(root, args["loading_cap"])
            parent.feed = eq.Amounts({c: n + capped * direction[c] for c, n in initial.items()})
            return dict(
                nodes=nodes,
                bracket=bracket,
                root=root,
                loading=capped,
                source_cap=args["loading_cap"],
                target_Pa=args["P"],
                pressure_residual_Pa=residual(root),
            )
        previous, start = nodes[-1], result
    raise ValueError(f"{record['identity']}: no positive-slope saturation bracket on declared loading grid")


def grid_states(stocks, loadings):
    """The liquid-parent grid at the declared stocks and loadings."""
    return [
        dict(
            key=f"grid:{stock}:{T}:{a}:{c}",
            T=round(313.15 + 10 * i, 2),
            stock=stock,
            a=a,
            c=c,
        )
        for stock in stocks
        for i in range(9)
        for T in [round(313.15 + 10 * i, 2)]
        for a in loadings
        for c in (1.05, 3.0)
    ]


def grid_axes(route, spec):
    """#337 rule (b) grid from the declared fitted stocks and data loadings: 0.1 mol/mol loading steps from 1e-5 to the
    largest data loading, and fitted concentrations within 1 wt% of the lowest of their group searched once, at that lowest."""
    loadings = route.config["loadings"]
    if not route.config["stocks"]:
        return [], []
    if loadings[0] != LOWEST_LOADING:
        raise ValueError("Part II grid declaration has a different minimum loading")
    top = loadings[-1]
    loadings = [LOWEST_LOADING] + [round(0.1 * k, 4) for k in range(1, math.ceil(top / 0.1 - 1e-9))] + [top]
    masses = {
        c["component_id"]: c["fixed"]["molar_mass"]["value"]["magnitude"]
        for c in epcsaft.parameters.document_mapping(spec.parameters)["components"]
    }
    amine = route.config["amine"]

    def weight(stock):
        return 100 * masses[amine] * stock[amine] / math.fsum(masses[c] * n for c, n in stock.items())

    stocks = []
    for stock in sorted(route.config["stocks"], key=weight):
        if not stocks or weight(stock) - weight(stocks[-1]) > 1.0:
            stocks.append(stock)
    return stocks, loadings


def states(route, spec):
    from .mea import MEARoute

    if isinstance(route, MEARoute):
        return route.phase_states()
    states = []
    for role in ("fitted", "comparisons"):
        for row in spec.inputs["observations"][role]:
            if row["constructor"] == "residual_excess_enthalpy":
                continue
            if row["constructor"] == "saturation_capped_addition_enthalpy":
                states.append(dict(key=row["identity"] + ":cap", cap_record=row["identity"]))
            for field in ("problem", "initial", "final", "bubble"):
                if field in row:
                    states.append(dict(key=row[field], problem=row[field]))
    states.extend(dict(key=r["problem"], problem=r["problem"]) for r in spec.inputs["observations"]["phase_states"])
    states.extend(grid_states(*grid_axes(route, spec)))
    return list({r["key"]: r for r in states}.values())


def stability_row(route, spec, state, scale, *, metadata=None, cap_from_prediction=False):
    from .mea import MEARoute

    if isinstance(route, MEARoute):
        return route.stability_row(spec, state, scale)
    if "cap_record" in state:
        record = next(
            r
            for role in ("fitted", "comparisons")
            for r in spec.inputs["observations"][role]
            if r["identity"] == state["cap_record"]
        )
        parent = copy.copy(spec.problems[record["initial"]])
        if cap_from_prediction:
            prediction = reg.predict(spec.model, spec.observation(record))
            if prediction.status.name != "Available":
                raise ValueError(prediction.message)
            args = record["arguments"]
            parent.feed = eq.Amounts({
                c: parent.feed.values.get(c, 0.0) + prediction.endpoint_loading * args["basis_amount"] * args["feed"].get(c, 0.0)
                for c in spec.parameters.component_ids
            })
            evidence = dict(loading=prediction.endpoint_loading)
        else:
            evidence = capped_feed(spec, record, parent)
        if metadata is not None:
            metadata["capped_feed"] = evidence
        bubble = None
    elif "binary_x" in state:
        water, amine = "water", route.config["amine"]
        feed = {water: 1 - state["binary_x"], amine: state["binary_x"]}
        parent = eq.Problem(
            T=state["T"],
            P=state["P"],
            feed=eq.Amounts(feed),
            phases=[eq.Phase("L", kind="liquid", support=list(feed))],
            row_tolerance=1e-10,
        )
        bubble = None
    elif "problem" in state:
        parent = copy.copy(spec.problems[state["problem"]])
        bubble = copy.copy(parent) if isinstance(parent.P, eq.Free) else None
        parent.phases = [copy.copy(parent.phases[0])]
        parent.phases[0].amount = eq.Free()
        parent.P = 1e5 if bubble is not None else parent.P
    else:
        template = next(p for p in spec.problems.values() if p.reactions)
        feed = dict(
            state["stock"],
            **{"carbon-dioxide": state["a"] * state["stock"][route.config["amine"]]},
        )
        parent = eq.Problem(
            T=state["T"],
            P=1e5,
            feed=eq.Amounts(feed),
            phases=[eq.Phase("L", kind="liquid", support=route.config["species"])],
            reactions=template.reactions,
            neutral_reference=template.neutral_reference,
            row_tolerance=template.row_tolerance,
        )
        bubble = copy.copy(parent)
        bubble.P = eq.Free(1e5)
        bubble.phases = list(parent.phases) + [
            eq.Phase(
                "V",
                kind="vapor",
                support=route.config["vapor_species"],
                amount=eq.Pinned(0.0),
            )
        ]
    if state.get("compressed"):
        bubble = copy.copy(parent)
        bubble.P = eq.Free(1e5)
        bubble.phases = list(parent.phases) + [
            eq.Phase(
                "V",
                kind="vapor",
                support=route.config["vapor_species"],
                amount=eq.Pinned(0.0),
            )
        ]
    item = reg.stability(
        spec.parameters,
        parent,
        scale=scale,
        **(dict(pressure_reference=bubble, pressure_ratio=state.get("c", 1.05)) if bubble else {}),
    )
    removed = set(eq.compile_problem(spec.model, item.problem).removed_species)
    if removed:
        # ponytail: remove when tannerpolley/epcsaft#24 excludes compiler-certified absent species.
        support = {i for i, v in enumerate(item.problem.feed.values) if v > 0}
        support.update(i for rx in item.problem.reactions for i, v in enumerate(rx.stoichiometry) if v != 0)
        support = sorted(support - removed)
        charges = {
            c["component_id"]: c["fixed"]["charge_number"]["value"]["magnitude"]
            for c in epcsaft.parameters.document_mapping(spec.parameters)["components"]
        }
        neutral = [i for i in support if charges[spec.parameters.component_ids[i]] == 0]
        trials = []
        for ids, kind in ((support, "Liquid"), (neutral, "Liquid"), (neutral, "Vapor")):
            phase = type(item.problem.phases[0])()
            phase.name, phase.kind, phase.support, phase.support_declared = (
                "feasible",
                getattr(type(phase.kind), kind),
                ids,
                True,
            )
            trials.append(phase)
        item.stability_options.trials = trials
    return item


def same_calculations(route, point, states):
    """Data-state key -> the first key whose search the Engine receives identically; grid keys differ by construction."""
    spec, first, same = route.bind(point), {}, {}
    for state in states:
        if state["key"].startswith("grid:"):
            continue
        try:
            item = stability_row(route, spec, state, 1.0)
        except Exception:
            continue  # measured on its own, where the refusal is recorded
        identity = json.dumps(
            calculation_declaration(
                [
                    item.problem,
                    item.pressure_reference,
                    item.pressure_ratio if item.pressure_reference is not None else None,
                    item.stability_options.trials,
                ]
            ),
            sort_keys=True,
        )
        same[state["key"]] = first.setdefault(identity, state["key"])
    return {key: source for key, source in same.items() if key != source}


class SuppliedTrials:
    """Evaluate retained trial compositions on the current liquid parent."""

    def __init__(self, spec, witnesses, *, compiled_support=True):
        self.spec = spec
        self.witnesses = witnesses
        self.compiled_support = compiled_support
        self.by_support = {}
        self.prepared = None

    def applicable(self, item, witnesses, support):
        phases, repeated, unique = [], [], {}
        for witness in witnesses:
            if not set(witness["support"]) <= support:
                continue
            kind = witness.get("kind", "Liquid" if len(witness["support"]) == len(self.spec.parameters.component_ids) else "Vapor")
            identity = (kind, tuple(witness["support"]), tuple(witness["composition"]), witness["packing"])
            i = unique.setdefault(identity, len(phases))
            repeated.append((i, witness))
            if i < len(phases):
                continue
            phase = type(item.problem.phases[0])()
            phase.name, phase.kind, phase.support_declared = "previous-split", getattr(type(phase.kind), kind), True
            phase.support, phase.composition_guess, phase.packing_guess = identity[1:]
            phases.append(phase)
        return phases, repeated, tuple(unique)

    def support(self, item):
        spec = self.spec
        if self.compiled_support:
            compiled = eq.compile_problem(spec.model, item.problem)
            return frozenset(range(len(spec.parameters.component_ids))) - set(compiled.removed_species)
        # The earlier screens offered all species present in the feed or reactions.
        return frozenset(i for i, amount in enumerate(item.problem.feed.values) if amount > 0) | frozenset(
            i for reaction in item.problem.reactions for i, value in enumerate(reaction.stoichiometry) if value
        )

    def evaluate(self, item, prediction, key):
        spec = self.spec
        support = self.support(item)
        if isinstance(self.witnesses, dict):
            witnesses = self.witnesses.get(key, ())
            phases, repeated, identities = self.applicable(item, witnesses, support)
        else:
            witnesses = self.witnesses
            if support not in self.by_support:
                self.by_support[support] = self.applicable(item, witnesses, support)
            phases, repeated, identities = self.by_support[support]
        if not witnesses:
            return {}
        excluded = len(witnesses) - len(repeated)
        if not phases:
            return dict(supplied_trial_counts=dict(available=0, unavailable=0, not_applicable=excluded))
        details = dict(supplied_available=False, supplied_minimum_tpd=None, supplied_trial_evidence=[])
        evaluated = 0
        try:
            parent = item.problem
            if prediction.pressure_reference is not None:
                parent.pressure = type(parent.pressure).fixed(prediction.pressure_reference.value * item.pressure_ratio)
            result = eq.solve_equilibrium(spec.model, parent)
            prepared_key = (parent.temperature.value, identities)
            if self.prepared is None or self.prepared[0] != prepared_key:
                self.prepared = prepared_key, eq.prepare_supplied_trials(spec.model, prepared_key[0], phases)
            options = eq.StabilityOptions()
            options.prepared_trials = self.prepared[1]
            report = eq.stability_test(eq.compile_problem(spec.model, parent), result, options)
            trials = [dict(evidence=t.evidence, resolved_descent=t.resolved_descent, quantities=jsonable(t.quantities), message=t.message)
                      for t in report.trials]
            pairs = ([(trials[i], witness) for i, witness in repeated] if len(trials) == len(phases)
                     else [(trial, None) for trial in trials])
            evaluated = sum(trial["evidence"] == "evaluated" for trial, _ in pairs)
            evidence = {}
            for trial, witness in pairs:
                if supplied_negative(trial):
                    side = trial["quantities"].get("density_side")
                    old = evidence.get(side)
                    if old is None or trial["quantities"]["tpd_over_rt"] < old["quantities"]["tpd_over_rt"]:
                        evidence[side] = dict(trial, phase=witness)
            details.update(
                supplied_parent_pressure_Pa=result.pressure,
                supplied_available=result.requested_tolerance_met and len(trials) == len(phases) and evaluated == len(repeated),
                supplied_minimum_tpd=min((trial["quantities"]["tpd_over_rt"] for trial, _ in pairs if trial["evidence"] == "evaluated"), default=None),
                supplied_trial_evidence=list(evidence.values()),
            )
        except (ValueError, RuntimeError, TypeError) as error:
            details["supplied_error"] = f"{type(error).__name__}: {error}"
        details["supplied_trial_counts"] = dict(available=evaluated, unavailable=len(repeated) - evaluated, not_applicable=excluded)
        return details


def native_search(route, spec, state, *, supplied=None, cap_from_prediction=False):
    wheel = verify()
    metadata = {}
    try:
        item = stability_row(route, spec, state, 1.0, metadata=metadata, cap_from_prediction=cap_from_prediction)
        prediction = reg.predict(spec.model, item)
        search = stability_payload(prediction)
        if prediction.stability is not None:
            search["witnesses"] = [
                dict(
                    resolved_descent=True,
                    kind=t.phase.kind.name,
                    density_side=t.quantities.get("density_side"),
                    support=list(t.phase.support),
                    composition=list(t.composition),
                    packing=math.exp(t.split_coordinates[-1]),
                )
                for t in prediction.stability.report.trials
                if t.resolved_descent and t.split_coordinates
            ]
        search["parent_kind"] = item.problem.phases[0].kind.name
        if supplied is not None:
            search["optimized_available"] = search["available"]
            search.update(supplied.evaluate(item, prediction, state["key"]))
            search["available"] &= search.get("supplied_available", True)
    except (ValueError, RuntimeError) as error:
        search = dict(
            status="Exception",
            message=f"{type(error).__name__}: {error}",
            available=False,
        )
    return dict(key=state["key"], wheel=wheel, search=search, **metadata)


def search_descent(search):
    value = search.get("value")
    optimized = search.get("optimized_available", search["available"]) and value is not None and value < 0
    minimum = search.get("supplied_minimum_tpd")
    return bool(optimized or (minimum is not None and minimum < 0)
                or any(map(supplied_negative, search.get("supplied_trials", ()))))


def search_class(search):
    if search_descent(search):
        return "descent"
    if not search["available"]:
        return "unavailable"
    if search.get("no_descent_in_trial_set"):
        return "searched, no instability"
    return "no resolved descent"


def measured_search_class(row):
    """Reclassify a held MEA measured-pressure record."""
    native = row["native_trials"]
    if any(t["descent"] for t in native) or any(t["source"] == "supplied" for t in row["witnesses"]):
        return "descent"
    if not (
        row["parent"]["physical_checks_pass"]
        and row["ion_rich_seed"]["strictly_positive"]
        and row["supplied_counts"].keys() == {"evaluated"}
        and row["ion_rich_result"]["evidence"] == "evaluated"
        and no_descent(bool(native), native)
    ):
        return "unavailable"
    return "searched, no instability"


def census_class(row):
    """Classify the MEA census from the held parent and its Engine trials."""
    if "failure" in row:
        return "unavailable"
    state, reports = row.get("final"), row.get("stability", [])
    if any(t["resolved_descent"] for r in reports for t in r["trials"]) or any(
        supplied_negative(t) for r in reports for t in r.get("supplied_trials", [])
    ):
        return "failed"
    if state is None or not state["success"] or not state["requested_tolerance_met"]:
        return "failed"
    if "raw_residuals" in state and (
        max(map(abs, state["raw_residuals"]), default=0.0) > 1e-10
        or state["reduced_hessian_minimum"] < 0
        or any(v <= 0 for v in state["pressure_density_derivatives"])
        or any(v < 0 for v in state["amounts"])
    ):
        return "failed"
    if (
        any(t["evidence"] != "evaluated" for r in reports for t in r.get("supplied_trials", []))
        or len(reports) != 1 or not reports[0]["completed"] or not reports[0]["trials"]
        or {t["phase"]["kind"] for t in reports[0]["trials"]} != {"liquid", "vapor"}
        or any(not t["optimizer"]["success"]
               or t["evidence"] in ("unresolved", "indeterminate", "negative_plane_without_positive_donor")
               for t in reports[0]["trials"])
        or "raw_residuals" not in state or row.get("bubble_pressure_Pa") is None
        or row.get("pressure_uncertainty_Pa") is None
    ):
        return "unresolved"
    dP = row["pressure_Pa"] - row["bubble_pressure_Pa"]
    if abs(dP) <= row["pressure_uncertainty_Pa"]:
        return "unresolved"
    expected = 2 if dP < 0 else 1
    if len(state["amounts"]) != expected:
        return "unresolved"
    return "passed-two-phase" if expected == 2 else "passed-single-liquid"


def phase_outcome(value, *, completion=False):
    if completion:
        if issue := value.get("engine_issue"):
            assert "#" in issue and issue.rsplit("#", 1)[1].isdigit()
            return "open Engine item"
        if value.get("pair"):
            return value["pair"]
        if value["parent_closed"] and value["native_complete"] and value["supplied_complete"] and not value["descent"]:
            return FINITE_NEGATIVE
        raise AssertionError(f"Search {value['key']} did not meet the completion rule")
    if any(q["confirmed"] for q in value.get("attempts", [])):
        return "confirmed split"
    if "instability" in value:
        return "unresolved phase identity" if value["instability"] == "resolved descent" else value["instability"]
    if value.get("search", {}).get("no_descent_in_trial_set"):
        return "finite search, no resolved descent"
    return "unresolved" if value.get("search", {}).get("completed") else "unavailable"


def no_descent(completed, trials):
    return bool(completed and trials) and all(
        t["evidence"] == "no_resolved_descent"
        and t["message"].startswith(("converged:", "Michelsen tangent-plane trial converged:"))
        and t.get("optimizer_success", True)
        and t.get("optimizer_tolerance_met") is not False
        and t.get("descent", t.get("resolved_descent")) is False
        for t in trials
    )


def supplied_complete(counts, excluded, declared):
    return (
        isinstance(counts, dict)
        and counts.keys() == {"evaluated"}
        and type(excluded) is int
        and type(declared) is int
        and 0 <= excluded <= declared
        and type(counts["evaluated"]) is int
        and counts["evaluated"] == declared - excluded
    )


R = epcsaft.GAS_CONSTANT_J_PER_MOL_K
# Match a recomputed root to the density at which the equilibrium was solved.
DENSITY_WINDOW = math.log(1.01)
COINCIDENCE = 1e-6
ERROR_TERMS = ("association_energy_estimate_over_rt",
               "feasibility_estimate_over_rt", "summation_estimate_over_rt")


def phase(model, T, P, amounts, rho, x, formulas):
    eos = model.state(T, rho=rho, x=x)
    return dict(T_K=T, amount_mol=amounts, density_mol_m3=rho, x=x, pressure_Pa=eos.pressure,
                pressure_residual_Pa=eos.pressure-P, relative_pressure_residual=(eos.pressure-P)/P, normalization_residual=math.fsum(x)-1,
                charge_residual=math.fsum(w*f['charge'] for w, f in zip(x, formulas, strict=True)))


def balances(feed, phases, formulas):
    inventory = sum(p['amount_mol']*np.array(p['x']) for p in phases)
    counts = np.array([[f.get(e, 0) for f in formulas] for e in 'CHNO'])
    atoms = counts @ (inventory-feed)
    scaled = atoms/(math.fsum(feed)*counts.max(axis=1))
    return dict(element_residual_mol=dict(zip('CHNO', atoms.tolist(), strict=True)), scaled_element_residual=dict(zip('CHNO', scaled.tolist(), strict=True)))


def scaled_pressure_error(residual, density, temperature):
    return abs(residual)/(density*R*temperature)


def phase_passed(p, P, tol, temperature=None):
    residual = p['pressure_residual_Pa']
    return (residual==p['pressure_Pa']-P and p.get('relative_pressure_residual',residual/P)==residual/P
            and p['normalization_residual']==math.fsum(p['x'])-1
            and max(abs(p['charge_residual']),abs(p['normalization_residual']),
                    scaled_pressure_error(residual,p['density_mol_m3'],p.get('T_K',temperature)))<=tol)


def phase_closure(value, pressure, tolerance, *, temperature=None):
    return bool(value.get('phases')) and all(phase_passed(p,pressure,tolerance,temperature) for p in value['phases']) and max(
        map(abs,value['balances']['scaled_element_residual'].values()))<=tolerance


def physical(spec, problem, result):
    ids = spec.parameters.component_ids
    formulas = [spec.spec['element_formulas'][c] for c in ids]
    T, P = result.temperature, result.pressure
    rows = [phase(spec.model, T, P, n, rho, result.phase_mole_fractions(i), formulas)
            for i, (n, rho) in enumerate(zip(result.amounts, result.molar_densities, strict=True))]
    feed = problem.feed.values
    if isinstance(feed, Mapping):
        feed = [feed.get(component, 0.0) for component in ids]
    residuals = balances(feed, rows, formulas)
    checks = dict(phases=rows,balances=residuals)
    return dict(checks,physical_checks_pass=phase_closure(checks,P,problem.row_tolerance),
                residuals=list(result.residuals),row_tolerance=problem.row_tolerance)


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


def _bind_search(route, point, witnesses):
    global _route, _spec, _supplied
    verify()
    _route, _spec = route, route.bind(point)
    _supplied = SuppliedTrials(_spec, witnesses) if witnesses else None


def _search(state):
    return native_search(_route, _spec, state, supplied=_supplied)


def measured_search(spec, row, bank):
    """Re-evaluate the recorded absolute-pressure request and its trial bank."""
    verify()
    ids = spec.parameters.component_ids
    template = next(problem for problem in spec.problems.values() if len(problem.phases) == 2)
    liquid = eq.Phase("L", kind="liquid", support=ids)
    vapor = eq.Phase("V", kind="vapor", support=ids[:3], amount=eq.Pinned(0.0))
    T, P = row["T_K"], row["P_Pa"]
    basis = dict(identity=row["identity"], T_K=T, P_Pa=P, feed_mol=row["feed_mol"])
    problem = eq.Problem(T=T, P=eq.Free(1e5), feed=eq.Amounts(row["feed_mol"]),
                         reactions=template.reactions, neutral_reference=template.neutral_reference,
                         row_tolerance=row["row_tolerance"], phases=[liquid, vapor])
    try:
        bubble = eq.solve_equilibrium(spec.model, problem)
        if not bubble.requested_tolerance_met:
            raise ValueError("Candidate bubble: " + bubble.message)
        problem.P = P
        liquid.composition_guess = list(bubble.phase_mole_fractions(0))
        liquid.packing_guess = bubble.packing_fractions[0]
        liquid_parent = P >= bubble.pressure
        if liquid_parent:
            problem.phases = [liquid]
        else:
            vapor.amount = eq.Free()
            vapor.composition_guess = {species: bubble.phase_mole_fractions(1)[i] for i, species in enumerate(ids[:3])}
            vapor.packing_guess = bubble.packing_fractions[1]
            problem.phases = [liquid, vapor]
        basis.update(bubble_Pa=bubble.pressure, declared_parent="liquid" if liquid_parent else "liquid-vapour")
        parent = eq.solve_equilibrium(spec.model, problem)
        if not parent.requested_tolerance_met or min(parent.amounts) <= 0:
            raise ValueError(parent.message)
        native = problem._native(spec.parameters)
        closure = physical(spec, native, parent)
        # The retained measured-pressure campaign normalized its pressure residual by P.
        closure["physical_checks_pass"] = all(
            max(abs(phase["relative_pressure_residual"]), abs(phase["charge_residual"]),
                abs(phase["normalization_residual"])) <= native.row_tolerance
            for phase in closure["phases"]
        ) and max(map(abs, closure["balances"]["scaled_element_residual"].values())) <= native.row_tolerance
        compiled = eq.compile_problem(spec.model, problem)
        options = eq.StabilityOptions()
        options.mode = type(options.mode).Full
        optimized = eq.stability_test(compiled, parent, options)

        inventory = [math.fsum(n * parent.phase_mole_fractions(i)[j] for i, n in enumerate(parent.amounts))
                     for j in range(len(ids))]
        amounts = dict(zip(ids, inventory, strict=True))
        extent = 0.5 * min(amounts["carbon-dioxide"], 0.5 * amounts["monoethanolamine"])
        change = {"carbon-dioxide": -1, "monoethanolamine": -2, "protonated-monoethanolamine": 1, "carbamate-anion": 1}
        rich = [amount + extent * change.get(species, 0) for species, amount in amounts.items()]
        total = math.fsum(rich)
        fractions = [amount / total for amount in rich]
        rho = spec.model.state(T, P=P, x=fractions, phase="liquid").molar_density
        witness = dict(support=list(range(len(ids))), composition=fractions, kind="Liquid",
                       packing=rho * spec.model._model.packing_fraction_coefficient(T, fractions))
        support = set(range(len(ids))) - set(compiled.removed_species)
        supplied = SuppliedTrials(spec, ())
        phases, repeated, _ = supplied.applicable(SimpleNamespace(problem=native), [*bank, witness], support)
        options = eq.StabilityOptions()
        options.prepared_trials = eq.prepare_supplied_trials(spec.model, T, phases)
        tested = eq.stability_test(compiled, parent, options).trials
        counts = Counter(tested[i].evidence for i, _ in repeated)
        descended = any(trial.resolved_descent for trial in optimized.trials) or any(
            supplied_negative(dict(evidence=tested[i].evidence, quantities=tested[i].quantities)) for i, _ in repeated)
        available = (closure["physical_checks_pass"] and optimized.completed and min(rich) > 0
                     and counts["evaluated"] == len(repeated) and bool(optimized.trials))
        return dict(basis, parent=closure, available=available, supplied_counts=dict(counts), descent=descended,
                    cause=None if available else "Inspect parent physical checks and native and supplied trial dispositions")
    except (ValueError, RuntimeError, IndexError, TypeError, AttributeError) as error:
        return dict(basis, available=False, descent=False, cause=f"{type(error).__name__}: {error}")


def _measured(row):
    return measured_search(_spec, row, _supplied.witnesses)


def _census(row):
    from .mea import CENSUS_FEED

    verify()
    spec = _spec
    T, P = row["temperature_K"], row["pressure_Pa"]
    model, ids = spec.model, spec.parameters.component_ids
    template = next(problem for problem in spec.problems.values() if len(problem.phases) == 2)
    amine, water = CENSUS_FEED
    feed = eq.Amounts({"monoethanolamine": amine, "water": water, "carbon-dioxide": row["loading"] * amine})
    liquid = eq.Phase("L", kind="liquid", support=ids)
    vapor = eq.Phase("V", kind="vapor", support=ids[:3])
    problem = eq.Problem(T=T, P=P, feed=feed, phases=[liquid, vapor], reactions=template.reactions,
                         neutral_reference=template.neutral_reference, row_tolerance=template.row_tolerance)
    record = {key: row[key] for key in ("index", "temperature_K", "pressure_Pa", "loading")}
    parent = eq.solve_equilibrium(model, problem)
    liquid_problem = copy.copy(problem)
    liquid_problem.phases = [liquid]
    liquid_parent = eq.solve_equilibrium(model, liquid_problem)
    if liquid_parent.success:
        bubble_problem = copy.copy(problem)
        bubble_problem.P = eq.Free(P)
        bubble_problem.phases = [
            eq.Phase("L", kind="liquid", support=ids, composition_guess=liquid_parent.phase_mole_fractions(0),
                     packing_guess=liquid_parent.packing_fractions[0]),
            eq.Phase("V", kind="vapor", support=ids[:3], amount=eq.Pinned(0.0)),
        ]
        bubble = eq.solve_equilibrium(model, bubble_problem)
        if bubble.success:
            criterion = bubble.convergence.criterion
            uncertainty = bubble.pressure * max(bubble.convergence.residual, bubble.convergence.floor or 0.0,
                                                criterion.value if criterion else 0.0)
            record.update(bubble_pressure_Pa=bubble.pressure, pressure_uncertainty_Pa=uncertainty)
            if P > bubble.pressure:
                problem, parent = liquid_problem, liquid_parent
            elif not parent.success:
                compositions = [[bubble.phase_mole_fractions(i)[ids.index(species)] for species in phase.support]
                                for i, phase in enumerate(problem.phases)]
                starts = [eq.EquilibriumStart(amounts=[bubble.amounts[0] * f, bubble.amounts[0] * (1 - f)],
                                               compositions=compositions, packing_fractions=bubble.packing_fractions)
                          for f in (0.5, 0.9)]
                batch = eq.solve_equilibrium_starts(model, problem, starts,
                    eq.EquilibriumWorkLimits(attempts=2, attempt_iterations=400, iterations=800))
                if batch.selected is not None:
                    parent = batch.results[batch.selected]
    record["final"] = final = dict(success=parent.success, requested_tolerance_met=parent.requested_tolerance_met)
    if parent.success:
        compiled = eq.compile_problem(model, problem)
        final.update(amounts=list(parent.amounts), raw_residuals=list(compiled.evaluate(parent.coordinates).values),
                     reduced_hessian_minimum=parent.reduced_hessian_minimum,
                     pressure_density_derivatives=[model.state(T, rho=rho, x=parent.phase_mole_fractions(i))
                                                   .pressure_density_derivative
                                                   for i, rho in enumerate(parent.molar_densities)])
        options = eq.StabilityOptions()
        trials = copy.copy(problem)
        trials.phases = [eq.Phase("trial-L", kind="liquid", support=ids),
                         eq.Phase("trial-V", kind="vapor", support=ids[:3])]
        options.trials = trials._native(model).phases
        optimized = eq.stability_test(compiled, parent, options)
        trials.phases = [eq.Phase("previous-split", kind=w["kind"].lower(), support=[ids[i] for i in w["support"]],
                                  composition_guess=w["composition"], packing_guess=w["packing"])
                         for w in _supplied.witnesses]
        options.evaluate_supplied_trials = True
        options.trials = trials._native(model).phases
        supplied = eq.stability_test(compiled, parent, options)
        record["stability"] = [dict(completed=optimized.completed, trials=[
            dict(resolved_descent=t.resolved_descent, evidence=t.evidence, optimizer=dict(success=t.optimizer.success),
                 phase=dict(kind=t.phase.kind.name.lower())) for t in optimized.trials
        ], supplied_trials=[dict(evidence=t.evidence, quantities=jsonable(t.quantities)) for t in supplied.trials])]
    record["classification"] = census_class(record)
    for report in record.get("stability", ()):
        trials = report["supplied_trials"]
        report["supplied_counts"] = dict(Counter(t["evidence"] for t in trials))
        report["supplied_trials"] = [t for t in trials if t["evidence"] != "evaluated" or supplied_negative(t)]
    return record


def reported_searches(amine, fit_set, route, point, target):
    from .fit import fingerprint, save
    from .model import REPORTED
    from .records import ROOT, read

    wheel, endpoint = verify(), fingerprint(point)
    spec = route.bind(point)
    declared = states(route, spec)
    keys = {state["key"] for state in declared}
    if amine == "mea":
        record = read(REPORTED / "MEA/screen/grid.json.gz")
        cases = [("grid", record["data"], {},
                  read(ROOT / "analyses/mea_parameter_bundle/results/reduced-refit/split-trials.json"))]
    else:
        if amine == "mdea":
            bank = read(ROOT / "analyses/mdea_mea_workflow/results/retransfer-343/binary-penalty/split-record.json")
        else:
            bank = route.load(route.config["split_record"])
        if amine == "amp":
            path = ROOT / "analyses/amp_transfer/results/retransfer-344-05e94210/campaign"
            saved = read(path / "new-witnesses.json.gz")
            manifest = read(path / "start-0/retreat-disposition.json")
            bank["trials"] += saved["additional"][:manifest["initial_trial_count"] - saved["initial"]]
            design = "AMP_free" if fit_set == "reported" else "AMP_fixed"
            domains = [(design, "selected", protocol) for protocol in ("native", "supplied")]
        else:
            domains = [(amine.upper(), "rebuild-441" if amine == "dea" else "selected", "declared")]
        witnesses = bank["trials"] + bank.get("supplied_trials", [])
        witnesses.sort(key=lambda witness: not witness.get("resolved_descent"))
        cases = []
        for design, lane, protocol in domains:
            record = read(REPORTED / design / "screen" / lane / protocol / "summary.json.gz")
            cases.append((protocol, record["rows"], record["aliases"], witnesses if protocol != "native" else []))
    checks = {}
    for protocol, retained, aliases, witnesses in cases:
        if {row["key"] for row in retained} != keys:
            raise ValueError(f"{amine} {fit_set} {protocol}: state request keys differ")
        if record["wheel"] != wheel or record["endpoint_fingerprint"] != endpoint:
            raise ValueError(f"{amine} {fit_set} {protocol}: phase baseline belongs to a different wheel or endpoint")
        distinct = [state for state in declared if state["key"] not in aliases]
        with ProcessPoolExecutor(max_workers=int(os.environ["AGENT_HEAVY_CORES"]), mp_context=get_context("fork"),
                                 initializer=_bind_search, initargs=(route, point, witnesses)) as pool:
            searches = {row["key"]: row["search"] for row in pool.map(_search, distinct, chunksize=4)}
        searches.update({key: searches[source] for key, source in aliases.items()})
        def identity(row):
            return search_class(row), row.get("status"), row.get("event")
        differences = [dict(key=row["key"], retained=identity(row), replayed=identity(searches[row["key"]]))
                       for row in retained if identity(row) != identity(searches[row["key"]])]
        save(target / f"{protocol}.json.gz", dict(wheel=wheel, endpoint_fingerprint=endpoint, rows=searches))
        checks[protocol] = dict(rows=len(searches), aliases=aliases, differences=differences)
    if amine == "mea":
        from .records import RESULTS

        folder = RESULTS / "mea/reported/phase"
        held = [row for path in sorted((folder / "measured").glob("*.json.gz")) for row in read(path)]
        bank = read(ROOT / "analyses/mea_parameter_bundle/results/reduced-refit/split-registry.json")["trials"]
        bank = [dict(witness, kind=witness["kind"].capitalize()) for witness in bank]
        census = read(folder / "screen/census-raw.json.gz")["data"]
        with ProcessPoolExecutor(max_workers=int(os.environ["AGENT_HEAVY_CORES"]), mp_context=get_context("fork"),
                                 initializer=_bind_search, initargs=(route, point, bank)) as pool:
            results = list(pool.map(_census, census, chunksize=4))
            measured = list(pool.map(_measured, held, chunksize=4))
        census_differences = [new["index"] for old, new in zip(census, results, strict=True)
                              if old["classification"] != new["classification"]]
        save(target / "census.json.gz", dict(wheel=wheel, endpoint_fingerprint=endpoint, rows=results))
        checks["census"] = dict(rows=len(results), differences=census_differences)
        fields = ("identity", "declared_parent", "P_Pa", "T_K", "available")
        differences = [new["identity"] for old, new in zip(held, measured, strict=True)
                       if any(old.get(key) != new.get(key) for key in fields)
                       or bool(old["witnesses"]) != new["descent"]]
        save(target / "measured.json.gz", dict(wheel=wheel, endpoint_fingerprint=endpoint, rows=measured))
        checks["measured"] = dict(rows=len(measured), differences=differences)
    return dict(protocols=checks)
